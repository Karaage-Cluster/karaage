# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import json

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters

import karaage.common as common
import karaage.common.aaf_rapid_connect as aaf_rapid_connect
from karaage.common.decorators import login_required
from karaage.common.forms import LoginForm
from karaage.people.emails import send_reset_password_email
from karaage.people.forms import PasswordChangeForm, PersonForm
from karaage.people.models import Person


@sensitive_post_parameters('password')
def login(request, username=None):
    error = ''
    redirect_to = reverse('index')
    if 'next' in request.GET:
        redirect_to = request.GET['next']

    if request.POST:

        form = LoginForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            person = Person.objects.authenticate(
                username=username, password=password)
            if person is not None:
                if person.is_active and not person.is_locked():
                    auth_login(request, person)
                    return HttpResponseRedirect(redirect_to)
                else:
                    error = 'User account is inactive or locked'
            else:
                error = 'Username or password was incorrect'
    else:
        form = LoginForm(initial={'username': username})

    return render(
        template_name='karaage/people/profile_login.html',
        context={
            'form': form,
            'next': redirect_to,
            'error': error,
        }, request=request)


def aaf_rapid_connect_login(request):
    redirect_to = reverse('index')
    if 'next' in request.GET:
        redirect_to = request.GET['next']
    error = None

    form = aaf_rapid_connect.AafInstituteForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            institute = form.cleaned_data['institute']
            url = aaf_rapid_connect.build_login_url(
                request, institute.saml_entityid
            )
            aaf_rapid_connect.setup_login_redirect(request, redirect_to)
            return HttpResponseRedirect(url)

    return render(
        template_name='karaage/people/profile_login_aaf_rapid_connect.html',
        context={'form': form, 'error': error, },
        request=request)


@login_required
def profile_personal(request):

    person = request.user
    project_list = person.projects.all()
    project_requests = []
    user_applications = []
    start, end = common.get_date_range(request)

    return render(
        template_name='karaage/people/profile_personal.html',
        context=locals(),
        request=request)


@login_required
def edit_profile(request):
    person = request.user
    form = PersonForm(request.POST or None, instance=person)
    if request.method == 'POST':
        if form.is_valid():
            person = form.save()
            assert person is not None
            messages.success(
                request, "User '%s' was edited succesfully" % person)
            return HttpResponseRedirect(person.get_absolute_url())

    return render(
        template_name='karaage/people/profile_edit.html',
        context={'person': person, 'form': form},
        request=request)


@sensitive_post_parameters('new1', 'new2')
@login_required
def password_change(request):

    person = request.user

    if request.POST:
        form = PasswordChangeForm(data=request.POST, person=person)

        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully")
            return HttpResponseRedirect(reverse('kg_profile'))
    else:
        form = PasswordChangeForm(person=person)

    return render(
        template_name='karaage/common/profile_password.html',
        context={'person': person, 'form': form},
        request=request)


@login_required
def password_request(request):
    person = request.user

    post_reset_redirect = reverse('kg_profile_reset_done')

    if request.method == "POST":
        send_reset_password_email(person)
        return HttpResponseRedirect(post_reset_redirect)

    var = {
        'person': person,
    }
    return render(
        template_name='karaage/common/profile_password_request.html',
        context=var,
        request=request)


@login_required
def password_request_done(request):
    person = request.user
    var = {
        'person': person,
    }
    return render(
        template_name='karaage/common/profile_password_request_done.html',
        context=var,
        request=request)


@csrf_exempt
def profile_aaf_rapid_connect(request):
    person = None
    verified_jwt = None
    if request.method == "POST":

        if 'assertion' not in request.POST:
            return HttpResponseBadRequest()

        assertion = request.POST['assertion']

        try:
            # Verifies signature and expiry time
            verified_jwt = jwt.decode(
                assertion,
                settings.AAF_RAPID_CONNECT_SECRET,
                audience=settings.AAF_RAPID_CONNECT_AUDIENCE,
                issuer=settings.AAF_RAPID_CONNECT_ISSUER,
            )
            messages.success(request, "It really worked")
        except jwt.JWTError as e:
            messages.error(request, f"Error: Could not decode token: {e}")

        request.session['arc_jwt'] = verified_jwt

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        if verified_jwt:
            attributes = verified_jwt['https://aaf.edu.au/attributes']
            saml_id = attributes['edupersontargetedid']

            try:
                person = Person.objects.get(saml_id=saml_id)
            except Person.DoesNotExist:
                pass

            if person is None:
                try:
                    email = attributes['mail']
                    person = Person.objects.get(email=email)
                except Person.DoesNotExist:
                    pass

        if person is not None:
            # We must set the model backend here manually as we skip
            # the call to auth.authenticate().
            request.user = person
            request.user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, person)

        url = request.session.get('arc_url', None)
        if url is not None and not is_safe_url(
            url=url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            url = None

        if url is not None:
            return HttpResponseRedirect(url)

    request.session['arc_url'] = None
    session_jwt = request.session.get('arc_jwt', None)

    if verified_jwt:
        verified_jwt = json.dumps(verified_jwt, indent=4)

    if session_jwt:
        session_jwt = json.dumps(session_jwt, indent=4)

    var = {
        'arc_url': settings.AAF_RAPID_CONNECT_URL,
        'person': person,
        'verified_jwt': verified_jwt,
        'session_jwt': session_jwt,
    }
    return render(
        template_name='karaage/people/profile_aaf_rapid_connect.html',
        context=var,
        request=request
    )
