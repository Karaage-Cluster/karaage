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
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator

from karaage.util import get_date_range
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.people.forms import PasswordChangeForm, PersonForm, LoginForm, PasswordResetForm
from karaage.machines.models import MachineCategory
from karaage.machines.forms import ShellForm
from karaage.applications.models import Application
from karaage.util import log_object as log

@login_required
def profile(request):

    person = request.user.get_profile()
    project_list = person.projects.all()
    project_requests = []
    user_applications = []
    start, end = get_date_range(request)

    if person.is_leader():
        leader = True
        leader_project_list = Project.objects.filter(leaders=person, is_active=True)

        for project in leader_project_list:
            for user_application in project.userapplication_set.filter(state=Application.WAITING_FOR_LEADER):
                user_applications.append(user_application)

    usage_list = person.usercache_set.filter(start=start, end=end)

    return render_to_response('people/profile.html', locals(), context_instance=RequestContext(request))


@login_required
def edit_profile(request):
    from admin import add_edit_user
    return add_edit_user(
        request,
        form_class=PersonForm,
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
            messages.success(request, 'Shell changed successfully')
            return HttpResponseRedirect(reverse('kg_user_profile'))

    else:
        shell_form = ShellForm()
        try:
            shell_form.initial = {'shell': person.loginShell}
        except:
            pass

    return render_to_response('people/profile_accounts.html', locals(), context_instance=RequestContext(request))


@login_required
def profile_software(request):
    person = request.user.get_profile()
    software_list = person.softwarelicenseagreement_set.all()
    return render_to_response(
        'people/profile_software.html',
        {'person': person, 'software_list': software_list},
        context_instance=RequestContext(request))


@login_required
def profile_projects(request):

    person = request.user.get_profile()
    project_list = person.project_set.all()
    leader_project_list = []

    if person.is_leader():
        leader_project_list = Project.objects.filter(leaders=person, is_active=True)

    return render_to_response('people/profile_projects.html', {'person': person, 'project_list': project_list, 'leader_project_list': leader_project_list}, context_instance=RequestContext(request))


@login_required
def user_detail(request, username):
    person = get_object_or_404(Person, user__username=username)
    if not person.can_view(request.user):
        return HttpResponseForbidden('<h1>Access Denied</h1><p>You do not have permission to view details about this user.</p>')
    return render_to_response('people/user_person_detail.html', locals(), context_instance=RequestContext(request))


@login_required
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

    messages.success(request, 'User flagged as left institution')
    return HttpResponseRedirect(person.get_absolute_url())


@login_required
def institute_users_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)
    if not institute.can_view(request.user):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_list = institute.person_set.all()
    return render_to_response('users/institute_user_list.html', locals(), context_instance=RequestContext(request))


@login_required
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


@login_required
def password_change_done(request):
    return render_to_response('people/password_change_done.html', context_instance=RequestContext(request))


def login(request, username=None):

    error = ''
    redirect_to = settings.LOGIN_REDIRECT_URL
    if 'next' in request.REQUEST:
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
                    person = user.get_profile()

                    person.set_password(password)
                    person.update_password = False
                    person.save()
                    messages.success(request, 'Password updated. New accounts activated.')
                    log(None, person, 2, 'Automatically updated passwords.')
                    return HttpResponseRedirect(redirect_to)
                else:
                    error = 'User account is locked'
            else:
                error = 'Username or passord was incorrect'
    else:
        form = LoginForm(initial = {'username': username})

    return render_to_response('registration/login.html', {
        'form': form,
        'next': redirect_to,
        'error': error,
        }, context_instance=RequestContext(request))


@login_required
def password_reset(request):
    post_reset_redirect = reverse('password_reset_done')

    if request.user.has_perm('people.change_person'):
        person_list = Person.active.all()
    if request.user.get_profile().is_leader():
        person_list = Person.active.filter(project__leaders=request.user.get_profile()).distinct()
    else:
        person_list = Person.objects.none()

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        form.fields['email'].queryset = person_list

        if form.is_valid():
            opts = {}
            opts['use_https'] = request.is_secure()
            opts['token_generator'] = default_token_generator
            opts['email_template_name'] = 'registration/password_reset_email.html'
            opts['domain_override'] = settings.ACCOUNTS_ORG_NAME
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = PasswordResetForm()
        form.fields['email'].queryset = person_list

    return render_to_response(
        'registration/password_reset_form.html',
        {'form': form},
        context_instance=RequestContext(request))


@login_required
def make_default(request, useraccount_id, project_id):
    person = request.user.get_profile()
    user_account = get_object_or_404(UserAccount, pk=useraccount_id, user=person)
    project = get_object_or_404(Project, pk=project_id)

    if request.method != 'POST':
        return HttpResponseRedirect(user_account.get_absolute_url())

    user_account.default_project = project
    user_account.save()
    user_account.user.save()
    messages.success(request, "Default project changed succesfully")
    log(request.user, user_account.user, 2, 'Changed default project to %s' % project.pid)
    return HttpResponseRedirect(user_account.get_absolute_url())
