from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import QuerySetPaginator
from django.db.models import Q
from django.contrib.sites.models import Site

import datetime
from django_common.util.filterspecs import Filter, FilterBar, DateFilter

from karaage.machines.models import UserAccount, MachineCategory
from karaage.requests.models import UserRequest, ProjectRequest
from karaage.projects.models import Project
from karaage.people.models import Person, Institute
from karaage.people.forms import UserForm
from karaage.machines.forms import UserAccountForm
from karaage.util.email_messages import *
from karaage.datastores import create_account
from accounts.util import log_object as log

@login_required
def index(request):
    
    return render_to_response('users/index.html', locals(), context_instance=RequestContext(request))


@login_required
def add_edit_user(request, username=None):
    site = Site.objects.get_current()
    
    if request.user.has_perm('people.add_person'):
        if username is None:
            person = False
        else:
            person = get_object_or_404(Person, user__username=username)
    else:   
        person = request.user.get_profile()

    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            if person:
                # edit
                person = form.save(person)
                request.user.message_set.create(message="User '%s' was edited succesfully" % person)
            else:
                #Add
                person = form.save()
                request.user.message_set.create(message="User '%s' was created succesfully" % person)

        
            return HttpResponseRedirect(person.get_absolute_url())

    else:
        form = UserForm()
        if person:
            # Fill form with initial     
            initial = person.__dict__
            for i in person.user.__dict__:
                initial[i] = person.user.__dict__[i]
            initial['institute'] = initial['institute_id']
            
            form.initial = initial

            
    return render_to_response('people/person_form.html', locals(), context_instance=RequestContext(request))


def user_list(request, queryset=Person.objects.all()):
    page_no = int(request.GET.get('page', 1))

    user_list = queryset
    institute_list = Institute.primary.all()

    if request.REQUEST.has_key('institute'):
        institute_id = int(request.GET['institute'])
        user_list = user_list.filter(institute=institute_id)

    if request.REQUEST.has_key('status'):
        user_list = user_list.filter(user__is_active=int(request.GET['status']))

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date_approved__')])
    user_list = user_list.filter(**m_params)

    if request.method == 'POST':
        new_data = request.POST.copy()
        terms = new_data['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(user__username__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term) | Q(comment__icontains=term) 
            query = query & q
        
        user_list = user_list.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'status', {1: 'Active', 0: 'Deleted'}))
    filter_list.append(Filter(request, 'institute', Institute.primary.all()))
    filter_list.append(DateFilter(request, 'date_approved'))
    filter_bar = FilterBar(request, filter_list)

    p = QuerySetPaginator(user_list, 50)
    page = p.page(page_no)
    locked_count = 0

    deleted_count = user_list.filter(user__is_active=0).count()
    locked_count = locked_count - deleted_count
    active_count = user_list.count() - deleted_count 

    return render_to_response('people/person_list.html', locals(), context_instance=RequestContext(request)) 

@login_required
def account_request_list(request):

    request_list = UserRequest.objects.filter(leader_approved=True)
    return render_to_response('users/accountrequest_list.html', locals(), context_instance=RequestContext(request)) 

account_request_list = permission_required('main.add_useraccount')(account_request_list)

def account_request_detail(request, ar_id):
    ar = get_object_or_404(UserRequest, pk=ar_id)

    person = ar.person
    project = ar.project

    return render_to_response('users/accountrequest_detail.html', locals(), context_instance=RequestContext(request))

account_request_detail = permission_required('main.add_useraccount')(account_request_detail)

def account_request_approve(request, ar_id):
    ar = get_object_or_404(UserRequest, pk=ar_id)

    person = ar.person
    project = ar.project
    machine_category = ar.machine_category

    project.users.add(person)

    person.activate()

    log(request.user, person, 2, 'Added to project %s' % project)
    log(request.user, project, 2, '%s added to project' % person)

    # Check to see if user has an account for the machine category
    # if not create one.
    if not person.has_account(machine_category):
        ua = create_account(person, project, machine_category)

    send_account_approved_email(ar)
    ar.delete()

    request.user.message_set.create(message="User '%s' approved succesfully and an email has been sent" % person)
    return HttpResponseRedirect(person.get_absolute_url())

account_request_approve = permission_required('main.add_useraccount')(account_request_approve)



def account_request_reject(request, ar_id):
    ar = get_object_or_404(UserRequest, pk=ar_id)

    person = ar.person
    user = person.user
    project = ar.project
    machine_category = ar.machine_category

    send_account_rejected_email(ar)
    
    ar.delete()

    log(request.user, person, 2, "Account rejected")

    if not person.is_active:
        person.delete()
        user.delete()

    request.user.message_set.create(message="User '%s' rejected succesfully and an email has been sent" % person)
        
    return HttpResponseRedirect(reverse('ac_account_request_list'))

account_request_reject = permission_required('main.add_useraccount')(account_request_reject)
    
@login_required
def add_edit_useraccount(request, username=None, useraccount_id=None):

    if username is None:
        # Edit
        user_account = get_object_or_404(UserAccount, pk=useraccount_id)
        user = user_account.user
    else:
        #Add
        user =  get_object_or_404(Person, user__username=username)
        user_account = False

    if request.method == 'POST':
        
        form = UserAccountForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            if user_account:
                # Edit
                 try:
                     test_user_account = UserAccount.objects.get(
                         username__exact=data['username'], machine_category=data['machine_category'], date_deleted__isnull=True)
                 except:
                     user_account.username = data['username']
                     user_account.machine_category = data['machine_category']
                     user_account.default_project = data['default_project']
                     user_account.save()
                 
                     request.user.message_set.create(message="User account for '%s' changed succesfully" % user_account.user)
                     
                     return HttpResponseRedirect(user.get_absolute_url())
                 
                 if test_user_account.username == user_account.username:
                     # didn't change
                     user_account.machine_category = data['machine_category']
                     user_account.default_project = data['default_project']
                     user_account.save()
                     request.user.message_set.create(message="User account for '%s' changed succesfully" % user_account.user)
                     return HttpResponseRedirect(user.get_absolute_url())
                 
                 username_error = True                                                                   
            else:
                #add
                try:
                    project = data['default_project']
                except:
                    project = None
                
                machine_category = data['machine_category']

                try:
                    test_user_account = UserAccount.objects.get(
                        username__exact=data['username'], machine_category=machine_category, date_deleted__isnull=True)
                except:

                    user_account = create_account(user, project, machine_category)
                    
                    request.user.message_set.create(message="User account for '%s' created succesfully" % user_account.user)
                    
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

    return render_to_response('machines/useraccount_form.html', locals(), context_instance=RequestContext(request))

add_edit_useraccount = permission_required('main.add_useraccount')(add_edit_useraccount)


@login_required
def delete_useraccount(request, useraccount_id):

    user_account = get_object_or_404(UserAccount, pk=useraccount_id)

    if request.method == 'POST':
        user_account.deactivate()
        request.user.message_set.create(message="User account for '%s' deleted succesfully" % user_account.user)
        return HttpResponseRedirect(user_account.get_absolute_url())
    else:
        
        return render_to_response('users/useraccount_confirm_delete.html', locals(), context_instance=RequestContext(request))

delete_useraccount = permission_required('main.delete_useraccount')(delete_useraccount)

@login_required
def no_default_list(request):

    useraccount_list = UserAccount.objects.filter(default_project__isnull=True).filter(date_deleted__isnull=True)

    return render_to_response('users/no_default_list.html', locals(), context_instance=RequestContext(request))


def no_account_list(request):

    users = Person.objects.all()
    user_id_list = []
    
    for u in users:
        for p in u.project_set.all():
            if not u.has_account(p.machine_category):
                user_id_list.append(u.id)


    return user_list(request, Person.objects.filter(id__in=user_id_list))


def wrong_default_list(request):
    users = Person.objects.filter(user__is_active=True)
    wrong = []
    for u in users:
        for ua in u.useraccount_set.all():
            d = False
            
            for p in ua.project_list():
                if p == ua.default_project:
                    d = True

            if not d:
                wrong.append(u.id)

    return user_list(request, Person.objects.filter(id__in=wrong))
    

@login_required
def make_default(request, useraccount_id, project_id):

    site = Site.objects.get_current()

    user_account = get_object_or_404(UserAccount, pk=useraccount_id)
    project = get_object_or_404(Project, pk=project_id)
    
    if site.name == 'admin':
        if not request.user.has_perm('main.change_useraccount'):
            return HttpResponseForbidden('<h1>Access Denied</h1>')
    if site.name == 'user':
        if not request.user == user_account.user.user:
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_account = get_object_or_404(UserAccount, pk=useraccount_id)
    project = get_object_or_404(Project, pk=project_id)

    user_account.default_project = project
    user_account.save()
    
    request.user.message_set.create(message="Default project changed succesfully")

    log(request.user, user_account.user, 2, 'Changed default project to %s' % project.pid)

    if site.name == 'admin':       
        return HttpResponseRedirect(user_account.get_absolute_url())
    if site.name == 'user':
        return HttpResponseRedirect(reverse('user_profile'))
    else:
        return HttpResponseRedirect('/')


@login_required
def locked_list(request):

    person_list = Person.active.all()
    ids = []
    for p in person_list:
        if p.is_locked():
            ids.append(p.id)

    return user_list(request, Person.objects.filter(id__in=ids))


@login_required       
def pending_requests(request):

    #Exclude requests that are pare of project requests
    exclude_ids = [ x.user_request.id for x in ProjectRequest.objects.all()]
    request_list = UserRequest.objects.filter(leader_approved=False).exclude(id__in=exclude_ids)

    return render_to_response('users/pending_requests.html', locals(), context_instance=RequestContext(request))



def struggling(request):

    today = datetime.date.today()
    days30 = today - datetime.timedelta(days=30)
    
    machine_category = MachineCategory.objects.get_default()
    user_accounts = machine_category.useraccount_set.select_related().filter(date_deleted__isnull=True).filter(date_created__lt=days30).filter(user__last_usage__isnull=True).order_by('-date_created')


    if request.REQUEST.has_key('institute'):
        institute_id = int(request.GET['institute'])
        user_accounts = user_accounts.filter(user__institute=institute_id)

    params = dict(request.GET.items())
    m_params = dict([(str(k), str(v)) for k, v in params.items() if k.startswith('date_created__')])
    user_accounts = user_accounts.filter(**m_params)


    page_no = int(request.GET.get('page', 1))

    filter_list = []
    filter_list.append(Filter(request, 'institute', Institute.primary.all()))
    filter_list.append(DateFilter(request, 'date_created'))
    filter_bar = FilterBar(request, filter_list)

    p = QuerySetPaginator(user_accounts, 50)
    page = p.page(page_no)

    return render_to_response('users/struggling.html', locals(), context_instance=RequestContext(request))
