# Copyright 2007-2010 VPAC
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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

import datetime
from andsome.util.filterspecs import Filter, FilterBar, DateFilter

from karaage.projects.models import Project
from karaage.people.models import Person, Institute
from karaage.machines.models import UserAccount, MachineCategory
from karaage.machines.forms import UserAccountForm, ShellForm
from karaage.util import log_object as log
from karaage.datastores import create_account


@login_required
def add_edit_user(request, form_class, template_name='people/person_form.html', redirect_url=None, username=None):
    PersonForm = form_class

    if request.user.has_perm('people.add_person'):
        if username is None:
            person = False
        else:
            person = get_object_or_404(Person, user__username=username)
    else:
        person = request.user.get_profile()
    
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            if person:
                # edit
                person = form.save(person)
                log(request.user, person, 2, "Changed details" % person)
                messages.success(request, "User '%s' was edited succesfully" % person)
            else:
                #Add
                person = form.save()
                messages.success(request, "User '%s' was created succesfully" % person)
                
            if redirect_url is None:
                return HttpResponseRedirect(person.get_absolute_url())
            else:
                return HttpResponseRedirect(redirect_url)
    else:
        form = PersonForm()
        if person:
            # Fill form with initial
            initial = person.__dict__
            for i in person.user.__dict__:
                initial[i] = person.user.__dict__[i]
            initial['institute'] = initial['institute_id']
            
            form.initial = initial
            
    return render_to_response(template_name, {'person': person, 'form': form}, context_instance=RequestContext(request))


@login_required
def user_list(request, queryset=Person.objects.select_related()):
    page_no = int(request.GET.get('page', 1))

    user_list = queryset

    if 'institute' in request.REQUEST:
        user_list = user_list.filter(institute=int(request.GET['institute']))

    if 'status' in request.REQUEST:
        user_list = user_list.filter(user__is_active=int(request.GET['status']))

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date_approved__')])
    user_list = user_list.filter(**m_params)

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(user__username__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term) | Q(comment__icontains=term)
            query = query & q

        user_list = user_list.filter(query)
        page_no = 1
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'status', {1: 'Active', 0: 'Deleted'}))
    filter_list.append(Filter(request, 'institute', Institute.active.all()))
    filter_list.append(DateFilter(request, 'date_approved'))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(user_list, 50)
    page = p.page(page_no)
    
    return render_to_response('people/person_list.html',
        {'page': page, 'filter_bar': filter_bar}, context_instance=RequestContext(request))


@permission_required('machines.add_useraccount')
def add_edit_useraccount(request, username=None, useraccount_id=None):
    username_error = False

    if username is None:
        # Edit
        user_account = get_object_or_404(UserAccount, pk=useraccount_id)
        user = user_account.user
    else:
        #Add
        user = get_object_or_404(Person, user__username=username)
        user_account = False

    if request.method == 'POST':
        
        form = UserAccountForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data
            if user_account:
                # Edit
                user_account.machine_category = data['machine_category']
                user_account.default_project = data['default_project']
                user_account.save()
                messages.success(request, "User account for '%s' changed succesfully" % user_account.user)
                return HttpResponseRedirect(user.get_absolute_url())
                
            else:
                #add
                try:
                    project = data['default_project']
                except:
                    project = None
                    
                machine_category = data['machine_category']
                
                try:
                    UserAccount.objects.get(
                        username__exact=user.username, machine_category=machine_category, date_deleted__isnull=True)
                except UserAccount.DoesNotExist:
                    user_account = create_account(user, project, machine_category)
                    messages.success(request, "User account for '%s' created succesfully" % user_account.user)
                    
                    return HttpResponseRedirect(user.get_absolute_url())
                username_error = True
    else:
        form = UserAccountForm()
        from django import forms
        form.initial['username'] = user.username
        if user_account:
            # Fill form with initial
            form.fields['default_project'] = forms.ModelChoiceField(queryset=user.project_set.all())
            form.initial = user_account.__dict__
            form.initial['default_project'] = form.initial['default_project_id']
            form.initial['machine_category'] = form.initial['machine_category_id']
            
    return render_to_response(
        'machines/useraccount_form.html',
        {'form': form, 'user_account': user_account, 'username_error': username_error},
        context_instance=RequestContext(request))


@permission_required('machines.delete_useraccount')
def delete_useraccount(request, useraccount_id):

    user_account = get_object_or_404(UserAccount, pk=useraccount_id)

    if request.method == 'POST':
        user_account.deactivate()
        messages.success(request, "User account for '%s' deleted succesfully" % user_account.user)
        return HttpResponseRedirect(user_account.get_absolute_url())
    else:
        
        return render_to_response('machines/useraccount_confirm_delete.html', locals(), context_instance=RequestContext(request))


@login_required
def no_default_list(request):
    useraccount_list = UserAccount.objects.filter(default_project__isnull=True).filter(date_deleted__isnull=True)
    return render_to_response('people/no_default_list.html', {'useraccount_list': useraccount_list}, context_instance=RequestContext(request))


@login_required
def no_account_list(request):
    users = Person.objects.all()
    user_id_list = []
    
    for u in users:
        for p in u.project_set.all():
            for mc in p.machine_categories.all():
                if not u.has_account(mc):
                    user_id_list.append(u.id)

    return user_list(request, Person.objects.filter(id__in=user_id_list))

    
@login_required
def wrong_default_list(request):
    users = Person.active.all()
    wrong = []
    for u in users:
        for ua in u.useraccount_set.filter(machine_category__id=1, date_deleted__isnull=True):
            d = False
            for p in ua.project_list():
                if p == ua.default_project:
                    d = True
            if not d:
                if not u.is_locked():
                    wrong.append(u.id)
    return user_list(request, Person.objects.filter(id__in=wrong))

    
@login_required
def make_default(request, useraccount_id, project_id):

    user_account = get_object_or_404(UserAccount, pk=useraccount_id)
    project = get_object_or_404(Project, pk=project_id)

    access = False
    if request.user.has_perm('machines.change_useraccount'):
        access = True

    if request.user == user_account.user.user:
        access = True

    if not access:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_account = get_object_or_404(UserAccount, pk=useraccount_id)
    project = get_object_or_404(Project, pk=project_id)

    user_account.default_project = project
    user_account.save()
    user_account.user.save()
    
    messages.success(request, "Default project changed succesfully")
    log(request.user, user_account.user, 2, 'Changed default project to %s' % project.pid)

    if 'next' in request.REQUEST:
        return HttpResponseRedirect(request.GET['next'])
    return HttpResponseRedirect(user_account.get_absolute_url())

    
@login_required
def locked_list(request):

    person_list = Person.active.all()
    ids = []
    for p in person_list:
        if p.is_locked():
            ids.append(p.id)

    return user_list(request, Person.objects.filter(id__in=ids))


@login_required
def struggling(request):

    today = datetime.date.today()
    days30 = today - datetime.timedelta(days=30)
    
    machine_category = MachineCategory.objects.get_default()
    user_accounts = machine_category.useraccount_set.select_related().filter(date_deleted__isnull=True).filter(date_created__lt=days30).filter(user__last_usage__isnull=True).order_by('-date_created')

    if 'institute' in request.REQUEST:
        institute_id = int(request.GET['institute'])
        user_accounts = user_accounts.filter(user__institute=institute_id)

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date_created__')])
    user_accounts = user_accounts.filter(**m_params)
    page_no = int(request.GET.get('page', 1))

    filter_list = []
    filter_list.append(Filter(request, 'institute', Institute.active.all()))
    filter_list.append(DateFilter(request, 'date_created'))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(user_accounts, 50)
    page = p.page(page_no)

    return render_to_response(
        'people/struggling.html',
        {'page': page, 'filter_bar': filter_bar},
        context_instance=RequestContext(request))


@login_required
def change_shell(request, useraccount_id):

    if not request.user.has_perm('people.change_person'):
        return HttpResponseForbidden('<h1>Access Denied</h1>')
    ua = get_object_or_404(UserAccount, pk=useraccount_id)
    
    if request.method == 'POST':
        shell_form = ShellForm(request.POST)
        if shell_form.is_valid():
            shell_form.save(user_account=ua)
            messages.success(request, 'Shell changed successfully')
            return HttpResponseRedirect(ua.get_absolute_url())
    else:
        
        return HttpResponseRedirect('/')
