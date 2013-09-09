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
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator

from karaage.util import get_date_range
from karaage.people.models import Person, authenticate
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.people.forms import PasswordChangeForm, PersonForm
from karaage.people.forms import LoginForm, PasswordResetForm
from karaage.machines.models import Account
from karaage.machines.forms import ShellForm
from karaage.util import log_object as log

from karaage.util.decorators import login_required
import karaage.util.saml as saml

@login_required
def profile(request):

    person = request.user
    project_list = person.projects.all()
    project_requests = []
    user_applications = []
    start, end = get_date_range(request)

    usage_list = person.personcache_set.filter(start=start, end=end)

    return render_to_response('people/profile.html', locals(), context_instance=RequestContext(request))


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

    return render_to_response('people/edit_profile.html',
            {'person': person, 'form': form},
            context_instance=RequestContext(request))


@login_required
def profile_accounts(request):

    person = request.user
    accounts = person.account_set.filter(date_deleted__isnull=True)

    return render_to_response('people/profile_accounts.html', locals(), context_instance=RequestContext(request))


@login_required
def profile_software(request):
    person = request.user
    software_list = person.softwarelicenseagreement_set.all()
    return render_to_response(
        'people/profile_software.html',
        {'person': person, 'software_list': software_list},
        context_instance=RequestContext(request))


@login_required
def profile_projects(request):

    person = request.user
    project_list = person.projects.all()
    leader_project_list = []

    if person.is_leader():
        leader_project_list = Project.objects.filter(leaders=person, is_active=True)

    return render_to_response('people/profile_projects.html', {'person': person, 'project_list': project_list, 'leader_project_list': leader_project_list}, context_instance=RequestContext(request))


@login_required
def user_detail(request, username):
    person = get_object_or_404(Person, username=username)
    if not person.can_view(request.user):
        return HttpResponseForbidden('<h1>Access Denied</h1><p>You do not have permission to view details about this user.</p>')
    return render_to_response('people/user_person_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_users_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)
    if not institute.can_view(request.user):
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_list = institute.person_set.all()
    return render_to_response('users/institute_user_list.html', locals(), context_instance=RequestContext(request))


@login_required
def password_change(request):

    person = request.user

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
    redirect_to = reverse('index')
    if 'next' in request.REQUEST:
        redirect_to = request.REQUEST['next']

    if request.POST:

        form = LoginForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            from django.contrib.auth import login
            person = authenticate(username=username, password=password)
            if person is not None:
                if person.is_active and not person.is_locked():
                    login(request, person.user)
                    return HttpResponseRedirect(redirect_to)
                else:
                    error = 'User account is inactive or locked'
            else:
                error = 'Username or password was incorrect'
    else:
        form = LoginForm(initial = {'username': username})

    return render_to_response('people/login.html', {
        'form': form,
        'next': redirect_to,
        'error': error,
        }, context_instance=RequestContext(request))


def saml_login(request):
    redirect_to = reverse('login_saml')
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

    return render_to_response('people/login_saml.html',
            {'form': form, 'error': error, 'saml_session': saml_session, },
            context_instance=RequestContext(request))


def saml_details(request):
    redirect_to = reverse('saml_details')
    saml_session = saml.is_saml_session(request)

    if request.method == 'POST':
        if 'login' in request.POST:
            if request.user.is_authenticated():
                person = request.user
                institute = person.institute
                if institute.saml_entityid:
                    redirect_to = reverse("saml_details")
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
                redirect_to = reverse("saml_details")
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

    return render_to_response('people/saml_detail.html',
            {'attrs': attrs, 'saml_session': saml_session,
                'person': person, },
            context_instance=RequestContext(request))

def logout(request, username=None):
    url = reverse("index")
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logout was successful.')
    return HttpResponseRedirect(url)


@login_required
def password_reset_request(request):
    post_reset_redirect = reverse('password_reset_done')

    if request.user.is_admin:
        person_list = Person.active.all()
    if request.user.is_leader():
        person_list = Person.active.filter(project__leaders=request.user).distinct()
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
def change_account_shell(request, account_id):
    person = request.user
    account = get_object_or_404(Account, pk=account_id, person=person)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('kg_user_profile_accounts'))

    shell_form = ShellForm(request.POST)
    if shell_form.is_valid():
        shell_form.save(account=account)
        messages.success(request, 'Shell changed successfully')
        return HttpResponseRedirect(reverse('kg_user_profile_accounts'))

@login_required
def make_default(request, account_id, project_id):
    person = request.user
    account = get_object_or_404(Account, pk=account_id, person=person)
    project = get_object_or_404(Project, pk=project_id)

    if request.method != 'POST':
        return HttpResponseRedirect(account.get_absolute_url())

    account.default_project = project
    account.save()
    messages.success(request, "Default project changed succesfully")
    log(request.user, account.user, 2, 'Changed default project to %s' % project.pid)
    return HttpResponseRedirect(account.get_absolute_url())
