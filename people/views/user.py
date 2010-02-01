from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings

from karaage.util import get_date_range
from karaage.people.models import Person, Institute
from karaage.projects.models import Project
from karaage.requests.models import ProjectCreateRequest
from karaage.people.forms import PasswordChangeForm, DelegateForm, BaseUserForm, LoginForm
from karaage.machines.models import MachineCategory
from karaage.machines.forms import ShellForm


@login_required
def profile(request):

    person = request.user.get_profile()
    
    project_list = person.project_set.all()
    project_requests = []
    account_requests = []

    start, end = get_date_range(request)

    if person.is_leader():
        leader = True
        leader_project_list = Project.objects.filter(leader=person, is_active=True)
        account_requests = []
        for project in leader_project_list:
            for user_request in project.projectjoinrequest_set.filter(leader_approved=False):
                account_requests.append(user_request)


    if person.is_active_delegate():
        project_requests = []
        #for project in person.institute.project_set.all():
        for project_request in ProjectCreateRequest.objects.filter(project__institute=person.institute):
            project_requests.append(project_request)
        
    
    if person.is_delegate():
        form = DelegateForm()
        d_ids = [p.id for p in person.institute.sub_delegates.all()]
        d_ids.append(person.id)
        
        delegates = Person.objects.filter(id__in=d_ids)
        from django import forms
        form.fields['active_delegate'] = forms.ModelChoiceField(queryset=delegates)
        try:
            form.initial['active_delegate'] = person.institute.active_delegate.id
        except:
            pass
        delegate = True

        if request.method == 'POST' and 'delegate-form' in request.POST:

            form = DelegateForm(request.POST)

            if form.is_valid():
                form.save(person.institute)
                return HttpResponseRedirect(reverse('kg_user_profile'))

    
    usage_list = person.usercache_set.filter(start=start, end=end)

    return render_to_response('people/profile.html', locals(), context_instance=RequestContext(request))
    

def edit_profile(request):
    from admin import add_edit_user
    return add_edit_user(
        request, 
        form_class=BaseUserForm,
        template_name='people/edit_profile.html',
        redirect_url=reverse('kg_user_profile'),
        username=request.user.get_profile().username)

@login_required
def profile_accounts(request):

    person = request.user.get_profile()
    user_account = person.get_user_account(MachineCategory.objects.get_default())

    if request.method == 'POST' and 'shell-form' in request.POST:

        shell_form = ShellForm(request.POST)

        if shell_form.is_valid():
            shell_form.save(user_account)
            request.user.message_set.create(message='Shell changed successfully')

            return HttpResponseRedirect(reverse('kg_user_profile'))

    else:
        shell_form = ShellForm()
        try:
            shell_form.initial = { 'shell': person.loginShell }
        except:
            pass
  
    return render_to_response('people/profile_accounts.html', locals(), context_instance=RequestContext(request))
    

@login_required
def profile_software(request):

    person = request.user.get_profile()
    
    software_list = person.softwarelicenseagreement_set.all()
  
    return render_to_response('people/profile_software.html', locals(), context_instance=RequestContext(request))
    


@login_required
def user_detail(request, username):

    person = get_object_or_404(Person, user__username=username)

    approved_viewers = []

    approved_viewers.append(person.id)
    
    try:
        approved_viewers.append(person.institute.delegate.id)
        approved_viewers.append(person.institute.active_delegate.id)
    except:
        pass

    for project in person.leader.all():
        approved_viewers.append(project.leader.id)
        approved_viewers.append(project.institute.delegate.id)
        approved_viewers.append(project.institute.active_delegate.id)
        
    for project in person.project_set.all():
        approved_viewers.append(project.leader.id)
        try:
            approved_viewers.append(project.institute.delegate.id)
            approved_viewers.append(project.institute.active_delegate.id)
        except:
            pass
    d = True
    if not request.user.get_profile().id in approved_viewers:
        return HttpResponseForbidden('<h1>Access Denied</h1><p>You do not have permission to view details about this user.</p>')

    
    return render_to_response('people/user_person_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def change_active_delegate(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)
    
    if not request.user.get_profile() == institute.delegate:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == 'POST':

        form = DelegateForm(request.POST)

        if form.is_valid():

            form.save()
            return HttpResponseRedirect(reverse('kg_user_profile'))


    return HttpResponseForbidden('<h1>Access Denied</h1>')
        

def flag_left(request, username):

    person = get_object_or_404(Person, user__username=username)

    Comment.objects.create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(person.__class__),
        object_id=person.id,
        comment='This user has left the institution',
        site=Site.objects.get(pk=1),
        valid_rating=True,
        is_public=False,
        is_removed=False,
    )

    request.user.message_set.create(message='User flagged as left institution')

    return HttpResponseRedirect(person.get_absolute_url())

    
@login_required
def institute_users_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    ids = [ institute.delegate.id , institute.active_delegate.id, ]

    if not request.user.get_profile().id in ids:
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_list = institute.person_set.all()

    return render_to_response('users/institute_user_list.html', locals(), context_instance=RequestContext(request))


def password_change(request):

    person = request.user.get_profile()
    
    if request.POST:
        form = PasswordChangeForm(request.POST)
        
        if form.is_valid():
            form.save(person)
            return HttpResponseRedirect(reverse('kg_user_password_done'))
    else:
        form = PasswordChangeForm()
        
    return render_to_response('people/user_password_form.html', {'form': form}, context_instance=RequestContext(request))


def password_change_done(request):
    
    return render_to_response('people/password_change_done.html', context_instance=RequestContext(request))


def login(request):

    error = ''
    redirect_to = settings.LOGIN_REDIRECT_URL
    if request.REQUEST.has_key('next'):
        redirect_to = request.REQUEST['next']

    if request.POST:

        form = LoginForm(request.POST)
        if form.is_valid():
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            from django.contrib.auth import login, authenticate
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(redirect_to)
                else:
                    error = 'User account is locked'
            else:
                error = 'Username or passord was incorrect'
    else:
        form = LoginForm()

    return render_to_response('registration/login.html', {
        'form': form,
        'next': redirect_to,
        'error': error,
        }, context_instance=RequestContext(request))



