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

from karaage.common import get_date_range
from karaage.people.emails import send_reset_password_email
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.people.forms import PasswordChangeForm, PersonForm
from karaage.people.forms import LoginForm
from karaage.machines.models import Account
from karaage.machines.forms import ShellForm
from karaage.common import log

from karaage.common.decorators import login_required
import karaage.common.saml as saml

@login_required
def profile(request):
    person = request.user
    return render_to_response('people/profile.html', locals(), context_instance=RequestContext(request))


@login_required
def profile_personal(request):

    person = request.user
    project_list = person.projects.all()
    project_requests = []
    user_applications = []
    start, end = get_date_range(request)

    usage_list = person.personcache_set.filter(start=start, end=end)

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

    return render_to_response('people/profile_projects.html',
            {'person': person, 'project_list': project_list,
                'leader_project_list': leader_project_list},
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

    return render_to_response('people/profile_password.html',
            {'person': person, 'form': form},
            context_instance=RequestContext(request))


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


def logout(request, username=None):
    url = reverse("index")
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logout was successful.')
    return HttpResponseRedirect(url)


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
    return render_to_response('people/profile_reset.html', var, context_instance=RequestContext(request))

@login_required
def password_request_done(request):
    person = request.user
    var = {
        'person': person,
    }
    return render_to_response('people/profile_reset_done.html', var, context_instance=RequestContext(request))
