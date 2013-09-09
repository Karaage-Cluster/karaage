# Copyright 2007-2013 VPAC
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
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

import datetime
from andsome.util.filterspecs import Filter, FilterBar, DateFilter

from karaage.util.decorators import admin_required
from karaage.projects.models import Project
from karaage.people.models import Person, Group
from karaage.people.emails import send_confirm_password_email
from karaage.people.forms import AddPersonForm, AdminPersonForm, AdminGroupForm
from karaage.institutes.models import Institute
from karaage.machines.models import Account
from karaage.machines.forms import AccountForm, ShellForm
from karaage.util import log_object as log


@admin_required
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


def add_user(request):
    return _add_edit_user(request, AddPersonForm, None)

def edit_user(request, username):
    return _add_edit_user(request, AdminPersonForm, username)

@admin_required
def user_list(request, queryset=None):
    if queryset is None:
        queryset=Person.objects.select_related()

    page_no = int(request.GET.get('page', 1))

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
    
    return render_to_response(
        'people/person_list.html',
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
        {'form': form, 'account': account, 'username_error': username_error},
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
    account_list = Account.objects.filter(default_project__isnull=True).filter(date_deleted__isnull=True)
    return render_to_response('people/no_default_list.html', {'account_list': account_list}, context_instance=RequestContext(request))


@admin_required
def no_account_list(request):
    person_id_list = []
    
    for u in Person.objects.all():
        for p in u.projects.all():
            for mc in p.machine_categories.all():
                if not u.has_account(mc):
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

    
@admin_required
def make_default(request, account_id, project_id):
    account = get_object_or_404(Account, pk=account_id)
    project = get_object_or_404(Project, pk=project_id)

    if request.method != 'POST':
        return HttpResponseRedirect(account.get_absolute_url())

    account.default_project = project
    account.save()
    messages.success(request, "Default project changed succesfully")
    log(request.user, account.person, 2, 'Changed default project to %s' % project.pid)
    return HttpResponseRedirect(account.get_absolute_url())

    
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
    
    accounts = Account.objects.select_related().filter(date_deleted__isnull=True).filter(date_created__lt=days30).filter(last_usage__isnull=True).order_by('-date_created')

    if 'institute' in request.REQUEST:
        institute_id = int(request.GET['institute'])
        accounts = accounts.filter(institute=institute_id)

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date_created__')])
    accounts = accounts.filter(**m_params)
    page_no = int(request.GET.get('page', 1))

    filter_list = []
    filter_list.append(Filter(request, 'institute', Institute.active.all()))
    filter_list.append(DateFilter(request, 'date_created'))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(accounts, 50)
    page = p.page(page_no)

    return render_to_response(
        'people/struggling.html',
        {'page': page, 'filter_bar': filter_bar},
        context_instance=RequestContext(request))


@admin_required
def change_account_shell(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    if request.method != 'POST':
        return HttpResponseRedirect(account.get_absolute_url())

    shell_form = ShellForm(request.POST)
    if shell_form.is_valid():
        shell_form.save(account=account)
        messages.success(request, 'Shell changed successfully')
        return HttpResponseRedirect(account.get_absolute_url())


@admin_required
def group_list(request, queryset=None):
    if queryset is None:
        queryset=Group.objects.select_related()

    page_no = int(request.GET.get('page', 1))

    group_list = queryset

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(name__icontains=term) | Q(description__icontains=term)
            query = query & q

        group_list = group_list.filter(query)
        page_no = 1
    else:
        terms = ""

    p = Paginator(group_list, 50)
    page = p.page(page_no)

    return render_to_response(
            'people/group_list.html',
            {'page': page, 'terms': terms},
            context_instance=RequestContext(request))


@admin_required
def _add_edit_group(request, form_class, group_name):
    GroupForm = form_class

    if group_name is None:
        group = None
    else:
        group = get_object_or_404(Group, name=group_name)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            if group:
                # edit
                group = form.save()
                messages.success(request, "Group '%s' was edited succesfully" % group)
            else:
                #Add
                group = form.save()
                messages.success(request, "Group '%s' was created succesfully" % group)

            return HttpResponseRedirect(group.get_absolute_url())
    else:
        form = GroupForm(instance=group)

    return render_to_response('people/group_form.html',
            {'group': group, 'form': form},
            context_instance=RequestContext(request))

def add_group(request):
    return _add_edit_group(request, AdminGroupForm, None)

def edit_group(request, group_name):
    return _add_edit_group(request, AdminGroupForm, group_name)
