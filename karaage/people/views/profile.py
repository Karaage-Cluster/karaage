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
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters

import karaage.common as common
import karaage.common.aaf_rapid_connect as aaf_rapid_connect
from karaage.common.decorators import login_required
from karaage.common.forms import LoginForm
from karaage.people.emails import send_reset_password_email
from karaage.people.forms import PasswordChangeForm, PersonForm
from karaage.people.models import Person


@sensitive_post_parameters("password")
def login(request, username=None):
    error = ""
    redirect_to = reverse("index")
    if "next" in request.GET:
        redirect_to = request.GET["next"]

    if request.POST:

        form = LoginForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            person = Person.objects.authenticate(username=username, password=password)
            if person is not None:
                if person.is_active and not person.is_locked():
                    auth_login(request, person)
                    return HttpResponseRedirect(redirect_to)
                else:
                    error = "User account is inactive or locked"
            else:
                error = "Username or password was incorrect"
    else:
        form = LoginForm(initial={"username": username})

    querystring = request.META.get("QUERY_STRING", "")

    return render(
        template_name="karaage/people/profile_login.html",
        context={
            "form": form,
            "next": redirect_to,
            "error": error,
            "querystring": querystring,
        },
        request=request,
    )


def aaf_rapid_connect_login(request):
    redirect_to = reverse("index")
    if "next" in request.GET:
        redirect_to = request.GET["next"]
    error = None

    form = aaf_rapid_connect.AafInstituteForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            institute = form.cleaned_data["institute"]
            url = aaf_rapid_connect.build_login_url(request, institute.saml_entityid)
            response = HttpResponseRedirect(url)
            response.set_cookie("arc_url", redirect_to)
            response.set_cookie("arc_required", True)
            return response

    querystring = request.META.get("QUERY_STRING", "")

    return render(
        template_name="karaage/people/profile_login_aaf_rapid_connect.html",
        context={"form": form, "error": error, "querystring": querystring},
        request=request,
    )


@login_required
def profile_personal(request):

    person = request.user
    project_list = person.projects.all()
    project_requests = []
    user_applications = []
    start, end = common.get_date_range(request)

    return render(template_name="karaage/people/profile_personal.html", context=locals(), request=request)


@login_required
def edit_profile(request):
    person = request.user
    form = PersonForm(request.POST or None, instance=person)
    if request.method == "POST":
        if form.is_valid():
            person = form.save()
            assert person is not None
            messages.success(request, "User '%s' was edited succesfully" % person)
            return HttpResponseRedirect(person.get_absolute_url())

    return render(
        template_name="karaage/people/profile_edit.html", context={"person": person, "form": form}, request=request
    )


@sensitive_post_parameters("new1", "new2")
@login_required
def password_change(request):

    person = request.user

    if request.POST:
        form = PasswordChangeForm(data=request.POST, person=person)

        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully")
            return HttpResponseRedirect(reverse("kg_profile"))
    else:
        form = PasswordChangeForm(person=person)

    return render(
        template_name="karaage/common/profile_password.html", context={"person": person, "form": form}, request=request
    )


@login_required
def password_request(request):
    person = request.user

    post_reset_redirect = reverse("kg_profile_reset_done")

    if request.method == "POST":
        send_reset_password_email(person)
        return HttpResponseRedirect(post_reset_redirect)

    var = {
        "person": person,
    }
    return render(template_name="karaage/common/profile_password_request.html", context=var, request=request)


@login_required
def password_request_done(request):
    person = request.user
    var = {
        "person": person,
    }
    return render(template_name="karaage/common/profile_password_request_done.html", context=var, request=request)


@csrf_exempt
def profile_aaf_rapid_connect(request):
    person = None
    verified_jwt = None

    if request.method == "POST":

        if "assertion" not in request.POST:
            return HttpResponseBadRequest()

        assertion = request.POST["assertion"]

        try:
            # Verifies signature and expiry time
            verified_jwt = jwt.decode(
                assertion,
                settings.AAF_RAPID_CONNECT_SECRET,
                audience=settings.AAF_RAPID_CONNECT_AUDIENCE,
                issuer=settings.AAF_RAPID_CONNECT_ISSUER,
                algorithms=["HS256"],
            )
        except jwt.PyJWTError as e:
            messages.error(request, f"Error: Could not decode token: {e}")

        arc_required = request.COOKIES.get("arc_required", False)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        if verified_jwt:
            attributes = verified_jwt["https://aaf.edu.au/attributes"]
            saml_id = attributes["edupersontargetedid"]

            try:
                person = Person.objects.get(saml_id=saml_id)
            except Person.DoesNotExist:
                pass

            if person is None:
                try:
                    email = attributes["mail"]
                    person = Person.objects.get(email=email)
                    person.saml_id = saml_id
                    person.save()
                except Person.DoesNotExist:
                    pass

        if person is None:
            auth_logout(request)
            if arc_required:
                messages.error(request, "Error: Could not find Karaage person")
        else:
            # We must set the model backend here manually as we skip
            # the call to auth.authenticate().
            request.user = person
            request.user.backend = "django.contrib.auth.backends.ModelBackend"
            auth_login(request, person)

        # We must setup the session after logging in / logging out.
        request.session["arc_jwt"] = verified_jwt

        url = request.COOKIES.get("arc_url", None)
        if url is not None:
            if not url_has_allowed_host_and_scheme(
                url=url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                url = None

        if url is not None:
            response = HttpResponseRedirect(url)
            response.delete_cookie("arc_url")
            response.delete_cookie("arc_required")
            return response

    session_jwt = request.session.get("arc_jwt", None)

    if verified_jwt:
        verified_jwt = json.dumps(verified_jwt, indent=4)

    if session_jwt:
        session_jwt = json.dumps(session_jwt, indent=4)

    var = {
        "arc_url": settings.AAF_RAPID_CONNECT_URL,
        "person": person,
        "verified_jwt": verified_jwt,
        "session_jwt": session_jwt,
    }
    return render(template_name="karaage/people/profile_aaf_rapid_connect.html", context=var, request=request)
