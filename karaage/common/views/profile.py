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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.contrib import messages

from karaage.common.forms import LoginForm
from karaage.common.decorators import login_required
import karaage.common.saml as saml
from karaage.people.models import Person


@login_required
def profile(request):
    person = request.user
    return render_to_response('common/profile.html', locals(), context_instance=RequestContext(request))


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

    return render_to_response('common/profile_login.html', {
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

    return render_to_response('common/profile_login_saml.html',
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

    return render_to_response('common/profile_saml.html',
            {'attrs': attrs, 'saml_session': saml_session,
                'person': person, },
            context_instance=RequestContext(request))


def logout(request, username=None):
    url = reverse("index")
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logout was successful.')
    return HttpResponseRedirect(url)
