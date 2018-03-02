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

from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

import karaage.common.saml as saml
from karaage.people.models import Person


class SamlUserMiddleware(MiddlewareMixin):
    """
    Middleware for utilizing Web-server-provided authentication.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``HTTP_PERSISTENT_ID`` request
    header.  If authentication is successful, the user is automatically logged
    in to persist the user in the session.

    The header used is configurable and defaults to ``HTTP_PERSISTENT_ID``.
    Subclass this class and change the ``header`` attribute if you need to use
    a different header.
    """

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django SAML user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the SamlUserMiddleware class.")

        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            return

        # Is this a shib session?
        if not saml.is_saml_session(request):
            return

        # Can we get the shib attributes we need?
        attrs, error = saml.parse_attributes(request)
        if error:
            return render(template_name='saml_error.html',
                          context={'shib_attrs': attrs},
                          request=request)

        # What is our persistent_id?
        saml_id = attrs['persistent_id']
        assert saml_id

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        try:
            person = Person.objects.get(saml_id=saml_id)
        except Person.DoesNotExist:
            return

        # User is valid.  Set request.user and persist user in the session
        # by logging the user in.
        request.user = person
        # We must set the model backend here manually as we skip
        # the call to auth.authenticate().
        request.user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, person)
