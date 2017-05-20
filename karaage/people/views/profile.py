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

from django.contrib.auth import login as auth_login
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.apps import apps
from django.views.decorators.debug import sensitive_post_parameters

from karaage.common.decorators import login_required
from karaage.people.models import Person
from karaage.people.emails import send_reset_password_email
from karaage.people.forms import PersonForm, PasswordChangeForm

import karaage.common as common
from karaage.common.forms import LoginForm
import karaage.common.saml as saml


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


def saml_login(request):
    redirect_to = reverse('index')
    if 'next' in request.GET:
        redirect_to = request.GET['next']
    error = None
    saml_session = saml.is_saml_session(request)

    form = saml.SAMLInstituteForm(request.POST or None)
    if request.method == 'POST':
        if 'login' in request.POST and form.is_valid():
            institute = form.cleaned_data['institute']
            url = saml.build_shib_url(
                request, redirect_to,
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
            Person.objects.get(saml_id=saml_id)
            # This should not happen, suggests a fault in the saml middleware
            error = "Shibboleth session established " \
                    "but you did not get logged in. "
        except Person.DoesNotExist:
            email = attrs['email']
            try:
                Person.objects.get(email=email)
                error = "Cannot log in with this shibboleth account. " \
                        "Please try using the Karaage login instead."
            except Person.DoesNotExist:
                if apps.is_installed("karaage.plugins.kgapplications"):
                    app_url = reverse('kg_application_new')
                    return HttpResponseRedirect(app_url)
                else:
                    error = "Cannot log in with shibboleth as " \
                            "we do not recognise your shibboleth id."

    return render(
        template_name='karaage/people/profile_login_saml.html',
        context={'form': form, 'error': error, 'saml_session': saml_session, },
        request=request)


def saml_details(request):
    redirect_to = reverse('kg_profile_saml')
    saml_session = saml.is_saml_session(request)

    if request.method == 'POST':
        if 'login' in request.POST:
            if request.user.is_authenticated():
                person = request.user
                institute = person.institute
                if institute.saml_entityid:
                    url = saml.build_shib_url(
                        request, redirect_to,
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
                return HttpResponseRedirect(redirect_to)
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

    return render(
        template_name='karaage/people/profile_saml.html',
        context={
            'attrs': attrs, 'saml_session': saml_session, 'person': person, },
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
        if person.has_usable_password():
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
