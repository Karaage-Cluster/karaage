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
from karaage.people.models import Person
from karaage.people.emails import send_bounced_warning
from karaage.people.emails import send_reset_password_email
from karaage.people.forms import AddPersonForm, AdminPersonForm, PersonForm
from karaage.people.forms import AdminPasswordChangeForm
from karaage.institutes.models import Institute

import karaage.common as common
from karaage.common.forms import LoginForm
import karaage.common.saml as saml


def login(request, username=None):
    error = ''
    redirect_to = reverse('index')
    if 'next' in request.REQUEST:
        redirect_to = request.REQUEST['next']

    if request.POST:

        form = LoginForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            from django.contrib.auth import login
            person = Person.objects.authenticate(username=username, password=password)
            if person is not None:
                if person.is_active and not person.is_locked():
                    login(request, person)
                    return HttpResponseRedirect(redirect_to)
                else:
                    error = 'User account is inactive or locked'
            else:
                error = 'Username or password was incorrect'
    else:
        form = LoginForm(initial = {'username': username})

    return render_to_response('people/profile_login.html', {
        'form': form,
        'next': redirect_to,
        'error': error,
        }, context_instance=RequestContext(request))


def saml_login(request):
    redirect_to = reverse('kg_profile_login_saml')
    if 'next' in request.REQUEST:
        redirect_to = request.REQUEST['next']
    error = None
    saml_session = saml.is_saml_session(request)

    form = saml.SAMLInstituteForm(request.POST or None)
    if request.method == 'POST':
        if 'login' in request.POST and form.is_valid():
            institute = form.cleaned_data['institute']
            url = saml.build_shib_url(request, redirect_to,
                    institute.saml_entityid)
            return HttpResponseRedirect(url)
        elif 'logout' in request.POST:
            if saml_session:
                url = saml.logout_url(request)
                return HttpResponseRedirect(url)
            else:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")
    elif request.user.is_authenticated():
        error = "You are already logged in."
    elif saml_session:
        attrs, error = saml.parse_attributes(request)
        saml_id = attrs['persistent_id']
        try:
            person = Person.objects.get(saml_id = saml_id)
            error = "Shibboleth session established but you did not get logged in."
        except Person.DoesNotExist:
            error = "Cannot log in with shibboleth as we do not know your shibboleth id."

    return render_to_response('people/profile_login_saml.html',
            {'form': form, 'error': error, 'saml_session': saml_session, },
            context_instance=RequestContext(request))


def saml_details(request):
    redirect_to = reverse('kg_profile_saml')
    saml_session = saml.is_saml_session(request)

    if request.method == 'POST':
        if 'login' in request.POST:
            if request.user.is_authenticated():
                person = request.user
                institute = person.institute
                if institute.saml_entityid:
                    url = saml.build_shib_url(request, redirect_to,
                            institute.saml_entityid)
                    return HttpResponseRedirect(url)
                else:
                    return HttpResponseBadRequest("<h1>Bad Request</h1>")
            else:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")

        elif 'register' in request.POST:
            if request.user.is_authenticated() and saml_session:
                person = request.user
                person = saml.add_saml_data(
                        person, request)
                person.save()
                return HttpResponseRedirect(url)
            else:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")

        elif 'logout' in request.POST:
            if saml_session:
                url = saml.logout_url(request)
                return HttpResponseRedirect(url)
            else:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")

        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


    attrs = {}
    if saml_session:
        attrs, _ = saml.parse_attributes(request)
        saml_session = True

    person = None
    if request.user.is_authenticated():
        person = request.user

    return render_to_response('people/profile_saml.html',
            {'attrs': attrs, 'saml_session': saml_session,
                'person': person, },
            context_instance=RequestContext(request))


@login_required
def profile_personal(request):

    person = request.user
    project_list = person.projects.all()
    project_requests = []
    user_applications = []
    start, end = common.get_date_range(request)

    return render_to_response('people/profile_personal.html', locals(), context_instance=RequestContext(request))


@login_required
def edit_profile(request):
    person = request.user
    form = PersonForm(request.POST or None, instance=person)
    if request.method == 'POST':
        if form.is_valid():
            person = form.save()
            assert person is not None
            messages.success(request, "User '%s' was edited succesfully" % person)
            return HttpResponseRedirect(person.get_absolute_url())

    return render_to_response('people/profile_edit.html',
            {'person': person, 'form': form},
            context_instance=RequestContext(request))


@login_required
def password_change(request):

    person = request.user

    if request.POST:
        form = PasswordChangeForm(request.POST)

        if form.is_valid():
            form.save(person)
            messages.success(request, "Password changed successfully")
            return HttpResponseRedirect(reverse('kg_profile'))
    else:
        form = PasswordChangeForm()

    return render_to_response('common/profile_password.html',
            {'person': person, 'form': form},
            context_instance=RequestContext(request))


@login_required
def password_request(request):
    person = request.user

    post_reset_redirect = reverse('kg_profile_reset_done')

    if request.method == "POST":
        if person.has_usable_password():
            send_reset_password_email(person)
            return HttpResponseRedirect(post_reset_redirect)

    var = {
        'person': person,
    }
    return render_to_response('common/profile_password_request.html', var, context_instance=RequestContext(request))


@login_required
def password_request_done(request):
    person = request.user
    var = {
        'person': person,
    }
    return render_to_response('common/profile_password_request_done.html', var, context_instance=RequestContext(request))


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
def user_list(request, queryset=None, template=None, context=None):
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

    new_context = {}
    if context is not None:
        new_context.update(context)

    new_context.update(
        {'page': page, 'filter_bar': filter_bar, 'terms': terms}
    )

    return render_to_response(template, new_context,
        context_instance=RequestContext(request))


@admin_required
def locked_list(request):

    person_list = Person.active.all()
    ids = []
    for p in person_list:
        if p.is_locked():
            ids.append(p.id)

    persons = Person.objects.filter(id__in=ids)
    context = { 'title': 'Locked' }
    return user_list(request, persons, "people/person_list_filtered.html", context)


@admin_required
def struggling(request):

    today = datetime.date.today()
    days30 = today - datetime.timedelta(days=30)

    persons = Person.objects.select_related()
    persons = persons.filter(date_deleted__isnull=True)
    persons = persons.filter(date_approved__lt=days30)
    persons = persons.filter(last_usage__isnull=True)
    persons = persons.order_by('-date_approved')

    context = { 'title': 'Struggling' }
    return user_list(request, persons, "people/person_struggling.html", context)

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
    
    return render_to_response('people/person_detail.html', locals(), context_instance=RequestContext(request))


@admin_required
def user_verbose(request, username):
    person = get_object_or_404(Person, username=username)

    from karaage.datastores import global_get_person_details
    person_details = global_get_person_details(person)

    from karaage.datastores import machine_category_get_account_details
    account_details = []
    for ua in person.account_set.filter(date_deleted__isnull=True):
        details = machine_category_get_account_details(ua)
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
