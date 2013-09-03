from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django_shibboleth.utils import parse_attributes
from karaage.people.models import Person
from django.shortcuts import render_to_response
from django.template import RequestContext


class SamlUserMiddleware(object):
    """
    Middleware for utilizing Web-server-provided authentication.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``HTTP_PERSISTENT_ID`` request header.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    The header used is configurable and defaults to ``HTTP_PERSISTENT_ID``.  Subclass
    this class and change the ``header`` attribute if you need to use a
    different header.
    """

    # Name of request header to grab username from.  This will be the key as
    # used in the request.META dictionary, i.e. the normalization of headers to
    # all uppercase and the addition of "HTTP_" prefix apply.
    header = "HTTP_PERSISTENT_ID"

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
        if request.user.is_authenticated():
            return

        # Is this a shib session?
        if 'HTTP_SHIB_SESSION_ID' not in request.META:
            return
        if not request.META['HTTP_SHIB_SESSION_ID']:
            return

        # Can we get the shib attributes we need?
        attrs, error = parse_attributes(request.META)
        if error:
            return render_to_response('shibboleth/attribute_error.html',
                                      {'shib_attrs': attrs},
                                      context_instance=RequestContext(request))

        # What is our persistent_id?
        saml_id = attrs['persistent_id']
        assert saml_id

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        try:
            person = Person.objects.get(saml_id = saml_id)
        except Person.DoesNotExist:
            return

        # User is valid.  Set request.user and persist user in the session
        # by logging the user in.
        request.user = person.user
        auth.login(request, person.user)
