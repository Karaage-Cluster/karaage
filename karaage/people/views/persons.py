# Copyright 2007-2014 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.conf import settings

from karaage.common.filterspecs import Filter, FilterBar, DateFilter
from karaage.common.decorators import admin_required, login_required
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project
from karaage.people.models import Person
from karaage.people.emails import send_confirm_password_email
from karaage.people.emails import send_bounced_warning
from karaage.people.emails import send_reset_password_email
from karaage.people.forms import AddPersonForm, AdminPersonForm
from karaage.people.forms import AdminPasswordChangeForm, AddProjectForm
from karaage.institutes.models import Institute
from karaage.machines.models import Account
from karaage.machines.forms import AccountForm, ShellForm
import karaage.common as common


def _add_edit_user(request, form_class, username):
    PersonForm = form_class

    if username is None:
        person = None
    else:
        person = get_object_or_404(Person, username=username)

    form = PersonForm(request.POST or None, instance=person)
    if request.method == 'POST':
        if form.is_valid():
            if person:
                # edit
                person = form.save()
                messages.success(request, "User '%s' was edited succesfully" % person)
                assert person is not None
            else:
                #Add
                person = form.save()
                messages.success(request, "User '%s' was created succesfully" % person)
                assert person is not None

            return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/person_form.html',
            {'person': person, 'form': form},
            context_instance=RequestContext(request))


@admin_required
def add_user(request):
    return _add_edit_user(request, AddPersonForm, None)

@admin_required
def edit_user(request, username):
    return _add_edit_user(request, AdminPersonForm, username)

@login_required
def user_list(request, queryset=None, template=None):
    if queryset is None:
        queryset=Person.objects.select_related()

    if template is None:
        template="people/person_list.html"

    if not common.is_admin(request):
        queryset = queryset.filter(pk=request.user.pk)

    user_list = queryset

    if 'institute' in request.REQUEST:
        user_list = user_list.filter(institute=int(request.GET['institute']))

    if 'status' in request.REQUEST:
        user_list = user_list.filter(is_active=int(request.GET['status']))

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date_approved__')])
    user_list = user_list.filter(**m_params)

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(username__icontains=term) | Q(short_name__icontains=term) | Q(full_name__icontains=term) | Q(comment__icontains=term)
            query = query & q

        user_list = user_list.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'status', {1: 'Active', 0: 'Deleted'}))
    filter_list.append(Filter(request, 'institute', Institute.active.all()))
    filter_list.append(DateFilter(request, 'date_approved'))
    filter_bar = FilterBar(request, filter_list)

    page_no = request.GET.get('page')
    paginator = Paginator(user_list, 50)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)
    
    return render_to_response(
        template,
        {'page': page, 'filter_bar': filter_bar, 'terms': terms},
        context_instance=RequestContext(request))


@admin_required
def add_edit_account(request, username=None, account_id=None):
    username_error = False

    if username is None:
        # Edit
        account = get_object_or_404(Account, pk=account_id)
        person = account.person
        username = account.username
    else:
        #Add
        person = get_object_or_404(Person, username=username)
        account = None

    if request.method == 'POST':
        
        form = AccountForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data
            if account:
                # Edit
                account.machine_category = data['machine_category']
                account.default_project = data['default_project']
                account.save()
                messages.success(request, "User account for '%s' changed succesfully" % account.person)
                return HttpResponseRedirect(person.get_absolute_url())
                
            else:
                #add
                try:
                    project = data['default_project']
                except:
                    project = None
                    
                machine_category = data['machine_category']
                
                try:
                    Account.objects.get(
                        username__exact=username, machine_category=machine_category, date_deleted__isnull=True)
                except Account.DoesNotExist:
                    account = Account.create(person, project, machine_category)
                    send_confirm_password_email(account.person)
                    messages.success(request, "User account for '%s' created succesfully" % account.person)
                    
                    return HttpResponseRedirect(person.get_absolute_url())
                username_error = True
    else:
        form = AccountForm()
        from django import forms
        form.initial['username'] = username
        if account:
            # Fill form with initial
            form.fields['default_project'] = forms.ModelChoiceField(queryset=person.projects.all())
            form.initial = account.__dict__
            form.initial['default_project'] = form.initial['default_project_id']
            form.initial['machine_category'] = form.initial['machine_category_id']
            
    return render_to_response(
        'machines/account_form.html',
        {'form': form, 'person': person, 'account': account, 'username_error': username_error},
        context_instance=RequestContext(request))


@admin_required
def delete_account(request, account_id):

    account = get_object_or_404(Account, pk=account_id)

    if request.method == 'POST':
        account.deactivate()
        messages.success(request, "User account for '%s' deleted succesfully" % account.person)
        return HttpResponseRedirect(account.get_absolute_url())
    else:
        
        return render_to_response('machines/account_confirm_delete.html', locals(), context_instance=RequestContext(request))


@admin_required
def no_default_list(request):
    persons = Person.objects.filter(account__isnull=False, account__default_project__isnull=True, account__date_deleted__isnull=True)
    return user_list(request, persons, "people/person_no_default_list.html")


@admin_required
def no_account_list(request):
    person_id_list = []

    for u in Person.objects.all():
        for project in u.projects.all():
            for pc in project.projectquota_set.all():
                if not u.has_account(pc.machine_category):
                    person_id_list.append(u.id)

    return user_list(request, Person.objects.filter(id__in=person_id_list))

    
@admin_required
def wrong_default_list(request):
    wrong = []
    for u in Person.active.all():
        for ua in u.account_set.filter(machine_category__id=1, date_deleted__isnull=True):
            d = False
            for p in ua.project_list():
                if p == ua.default_project:
                    d = True
            if not d:
                if not u.is_locked():
                    wrong.append(u.id)
    return user_list(request, Person.objects.filter(id__in=wrong))

    
@login_required
def make_default(request, account_id, project_id):
    if common.is_admin(request):
        account = get_object_or_404(Account, pk=account_id)
        redirect = account.get_absolute_url()
    else:
        account = get_object_or_404(Account, pk=account_id, person=request.user)
        redirect = reverse("kg_profile_projects")

    project = get_object_or_404(Project, pid=project_id)
    if request.method != 'POST':
        return HttpResponseRedirect(redirect)

    account.default_project = project
    account.save()
    messages.success(request, "Default project changed succesfully")
    common.log(request.user, account.person, 2, 'Changed default project to %s' % project.pid)
    return HttpResponseRedirect(redirect)

    
@admin_required
def locked_list(request):

    person_list = Person.active.all()
    ids = []
    for p in person_list:
        if p.is_locked():
            ids.append(p.id)

    return user_list(request, Person.objects.filter(id__in=ids))


@admin_required
def struggling(request):

    today = datetime.date.today()
    days30 = today - datetime.timedelta(days=30)

    persons = Person.objects.select_related()
    persons = persons.filter(date_deleted__isnull=True)
    persons = persons.filter(date_approved__lt=days30)
    persons = persons.filter(last_usage__isnull=True)
    persons = persons.order_by('-date_approved')

    return user_list(request, persons, "people/person_struggling.html")

@login_required
def change_account_shell(request, account_id):
    if common.is_admin(request):
        account = get_object_or_404(Account, pk=account_id)
        redirect = account.get_absolute_url()
    else:
        account = get_object_or_404(Account, pk=account_id, person=request.user)
        redirect = reverse("kg_profile_accounts")

    account = get_object_or_404(Account, pk=account_id)
    if request.method != 'POST':
        return HttpResponseRedirect(redirect)

    shell_form = ShellForm(request.POST)
    if shell_form.is_valid():
        shell_form.save(account=account)
        messages.success(request, 'Shell changed successfully')
        return HttpResponseRedirect(redirect)

@admin_required
def delete_user(request, username):

    person = get_object_or_404(Person, username=username)

    if request.method == 'POST':
        deleted_by = request.user
        person.deactivate(deleted_by)
        messages.success(request, "User '%s' was deleted succesfully" % person)
        return HttpResponseRedirect(person.get_absolute_url())
        
    return render_to_response('people/person_confirm_delete.html', locals(), context_instance=RequestContext(request))


@login_required
def user_detail(request, username):
    
    person = get_object_or_404(Person, username=username)
    if not person.can_view(request):
        return HttpResponseForbidden('<h1>Access Denied</h1><p>You do not have permission to view details about this user.</p>')

    my_projects = person.projects.all()
    my_pids = [p.pid for p in my_projects]
    
    #Add to project form
    form = AddProjectForm(request.POST or None)
    if request.method == 'POST':
        # Post means adding this user to a project
        if form.is_valid():
            project = form.cleaned_data['project']
            add_user_to_project(person, project)
            messages.success(request, "User '%s' was added to %s succesfully" % (person, project))
            common.log(request.user, project, 2, '%s added to project' % person)

            return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/person_detail.html', locals(), context_instance=RequestContext(request))

@admin_required
def user_verbose(request, username):
    person = get_object_or_404(Person, username=username)

    from karaage.datastores import get_person_details
    person_details = get_person_details(person)

    from karaage.datastores import get_account_details
    account_details = []
    for ua in person.account_set.filter(date_deleted__isnull=True):
        details = get_account_details(ua)
        account_details.append(details)

    return render_to_response('people/person_verbose.html', locals(), context_instance=RequestContext(request))

@admin_required
def activate(request, username):
    person = get_object_or_404(Person, username=username, is_active=False)

    if request.method == 'POST':
        approved_by = request.user
        person.activate(approved_by)
        return HttpResponseRedirect(reverse('kg_person_password', args=[person.username]))
    
    return render_to_response('people/person_reactivate.html', {'person': person}, context_instance=RequestContext(request))


@admin_required
def password_change(request, username):
    person = get_object_or_404(Person, username=username)
    
    if request.POST:
        form = AdminPasswordChangeForm(request.POST)
        
        if form.is_valid():
            form.save(person)
            messages.success(request, "Password changed successfully")
            if person.is_locked():
                person.unlock()
            return HttpResponseRedirect(person.get_absolute_url())
    else:
        form = AdminPasswordChangeForm()
        
    return render_to_response('people/person_password.html', {'person': person, 'form': form}, context_instance=RequestContext(request))


@admin_required
def lock_person(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.lock()
        messages.success(request, "%s's account has been locked" % person)
        return HttpResponseRedirect(person.get_absolute_url())
    return render_to_response('people/person_confirm_lock.html', locals(), context_instance=RequestContext(request))


@admin_required
def unlock_person(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.unlock()
        messages.success(request, "%s's account has been unlocked" % person)
        return HttpResponseRedirect(person.get_absolute_url())
    return render_to_response('people/person_confirm_unlock.html', locals(), context_instance=RequestContext(request))


@admin_required
def bounced_email(request, username):
    person = get_object_or_404(Person, username=username)
    if request.method == 'POST':
        person.lock()
        send_bounced_warning(person)
        messages.success(request, "%s's account has been locked and emails have been sent" % person)
        common.log(request.user, person, 2, 'Emails sent to project leaders and account locked')
        for ua in person.account_set.all():
            ua.change_shell(ua.previous_shell)
            ua.change_shell(settings.BOUNCED_SHELL)
        return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/person_bounced_email.html', locals(), context_instance=RequestContext(request))


@admin_required
def person_logs(request, username):
    obj = get_object_or_404(Person, username=username)
    breadcrumbs = []
    breadcrumbs.append( ("People", reverse("kg_person_list")) )
    breadcrumbs.append( (unicode(obj), reverse("kg_person_detail", args=[obj.username])) )
    return common.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, username):
    obj = get_object_or_404(Person, username=username)
    breadcrumbs = []
    breadcrumbs.append( ("People", reverse("kg_person_list")) )
    breadcrumbs.append( (unicode(obj), reverse("kg_person_detail", args=[obj.username])) )
    return common.add_comment(request, breadcrumbs, obj)

@login_required
def password_request(request, username):
    person = get_object_or_404(Person, username=username)

    post_reset_redirect = reverse('kg_person_reset_done', args=[person.username])

    if not person.can_view(request):
        return HttpResponseForbidden('<h1>Access Denied</h1><p>You do not have permission to view details about this user.</p>')

    if request.method == "POST":
        if person.has_usable_password():
            send_reset_password_email(person)
            return HttpResponseRedirect(post_reset_redirect)

    var = {
        'person': person,
    }
    return render_to_response('people/person_password_request.html', var, context_instance=RequestContext(request))

@login_required
def password_request_done(request, username):
    person = get_object_or_404(Person, username=username)
    var = {
        'person': person,
    }
    return render_to_response('people/person_password_request_done.html', var, context_instance=RequestContext(request))
