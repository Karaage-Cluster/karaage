# Copyright 2015 VPAC
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

""" This file implements a state machine for the views. """

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.contrib import messages

from karaage.common import log
import karaage.common as common

from ..models import Application


def get_url(request, application, roles, label=None):
    """ Retrieve a link that will work for the current user. """
    args = []
    if label is not None:
        args.append(label)

    # don't use secret_token unless we have to
    if 'is_admin' in roles:
        # Administrators can access anything without secrets
        require_secret = False
    elif 'is_applicant' not in roles:
        # we never give secrets to anybody but the applicant
        require_secret = False
    elif not request.user.is_authenticated():
        # If applicant is not logged in, we redirect them to secret URL
        require_secret = True
    elif request.user != application.applicant:
        # If logged in as different person, we redirect them to secret
        # URL. This could happen if the application was open with a different
        # email address, and the applicant is logged in when accessing it.
        require_secret = True
    else:
        # otherwise redirect them to URL that requires correct login.
        require_secret = False

    # return required url
    if not require_secret:
        url = reverse(
            'kg_application_detail',
            args=[application.pk, application.state] + args)
    else:
        url = reverse(
            'kg_application_unauthenticated',
            args=[application.secret_token, application.state] + args)
    return url


def get_admin_email_link(application):
    """ Retrieve a link that can be emailed to the administrator. """
    url = '%s/applications/%d/' % (settings.ADMIN_BASE_URL, application.pk)
    is_secret = False
    return url, is_secret


def get_registration_email_link(application):
    """ Retrieve a link that can be emailed to the logged other users. """
    url = '%s/applications/%d/' % (
        settings.REGISTRATION_BASE_URL, application.pk)
    is_secret = False
    return url, is_secret


def get_email_link(application):
    """ Retrieve a link that can be emailed to the applicant. """
    # don't use secret_token unless we have to
    if (application.content_type.model == 'person' and
            application.applicant.has_usable_password()):
        url = '%s/applications/%d/' % (
            settings.REGISTRATION_BASE_URL, application.pk)
        is_secret = False
    else:
        url = '%s/applications/%s/' % (
            settings.REGISTRATION_BASE_URL, application.secret_token)
        is_secret = True
    return url, is_secret


class StateMachine(object):
    """ State machine, for processing states. """

    ##################
    # PUBLIC METHODS #
    ##################

    def __init__(self):
        self._first_state = None
        self._states = {}
        super(StateMachine, self).__init__()

    def add_state(self, state, state_id, actions):
        """ Add a state to the list. The first state added becomes the initial
        state. """
        self._states[state_id] = state, actions

    def set_first_state(self, state_id):
        self._first_state = state_id

    def get_state(self, application):
        if application.state not in self._states:
            raise RuntimeError("Invalid state '%s'" % application.state)
        state, _ = self._states[application.state]
        return state

    def start(self, request, application, extra_roles=None):
        """ Continue the state machine at first state. """
        # Get the authentication of the current user
        roles = self._get_roles_for_request(request, application)
        if extra_roles is not None:
            roles.update(extra_roles)

        # Ensure current user is authenticated. If user isn't applicant,
        # leader, delegate or admin, they probably shouldn't be here.
        if 'is_authorised' not in roles:
            return HttpResponseForbidden('<h1>Access Denied</h1>')

        # Sanity check
        if self._first_state is None:
            raise RuntimeError("First state not set.")

        # Go to first state.
        return self._next(request, application, roles, self._first_state)

    def process(
            self, request, application,
            expected_state, label, extra_roles=None):
        """ Process the view request at the current state. """

        # Get the authentication of the current user
        roles = self._get_roles_for_request(request, application)
        if extra_roles is not None:
            roles.update(extra_roles)

        # Ensure current user is authenticated. If user isn't applicant,
        # leader, delegate or admin, they probably shouldn't be here.
        if 'is_authorised' not in roles:
            return HttpResponseForbidden('<h1>Access Denied</h1>')

        # If user didn't supply state on URL, redirect to full URL.
        if expected_state is None:
            url = get_url(request, application, roles, label)
            return HttpResponseRedirect(url)

        # Check that the current state is valid.
        if application.state not in self._states:
            raise RuntimeError("Invalid state '%s'" % application.state)

        # If state user expected is different to state we are in, warn user
        # and jump to expected state.
        if expected_state != application.state:
            # post data will be lost
            if request.method == "POST":
                messages.warning(
                    request,
                    "Discarding request and jumping to current state.")
            # note we discard the label, it probably isn't relevant for new
            # state
            url = get_url(request, application, roles)
            return HttpResponseRedirect(url)

        # Get the current state for this application
        state, actions = self._states[application.state]

        # Finally do something
        if request.method == "GET":
            # if method is GET, state does not ever change.
            response = state.view(
                request, application, label, roles, actions.keys())
            assert isinstance(response, HttpResponse)
            return response

        elif request.method == "POST":
            # if method is POST, it can return a HttpResponse or a string
            response = state.view(
                request, application, label, roles, actions.keys())
            if isinstance(response, HttpResponse):
                # If it returned a HttpResponse, state not changed, just
                # display
                return response
            else:
                # If it returned a string, lookit up in the actions for this
                # state
                if response not in actions:
                    raise RuntimeError(
                        "Invalid response '%s' from state '%s'"
                        % (response, state))
                next_state_key = actions[response]
                # Go to the next state
                return self._next(request, application, roles, next_state_key)

        else:
            # Shouldn't happen, user did something weird
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

    ###################
    # PRIVATE METHODS #
    ###################
    @staticmethod
    def _get_roles_for_request(request, application):
        """ Check the authentication of the current user. """
        roles = application.get_roles_for_person(request.user)

        if common.is_admin(request):
            roles.add("is_admin")
            roles.add('is_authorised')

        return roles

    def _next(self, request, application, roles, state_key):
        """ Continue the state machine at given state. """
        # we only support state changes for POST requests
        if request.method == "POST":
            # If next state is a transition, process it
            while isinstance(state_key, Transition):
                state_key = state_key.get_next_state(
                    request, application, roles)

            # lookup next state
            if state_key not in self._states:
                raise RuntimeError("Invalid state '%s'" % state_key)
            state, _ = self._states[state_key]

            # enter that state
            state.enter_state(request, application)
            application.state = state_key
            application.save()

            # log details
            log.change(application.application_ptr, "state: %s" % state.name)

            # redirect to this new state
            url = get_url(request, application, roles)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


class State(object):
    """ A abstract class that is the base for all application states. """
    name = "Abstract State"

    def __init__(self):
        self.context = {}

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        pass

    def view(self, request, application, label, roles, actions):
        """ Django view method. We provide a default detail view for
        applications. """

        # We only provide a view for when no label provided
        if label is not None:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # only certain actions make sense for default view
        tmp_actions = []
        if 'reopen' in actions:
            tmp_actions.append("reopen")
        if 'cancel' in actions:
            tmp_actions.append("cancel")
        if 'duplicate' in actions:
            tmp_actions.append("duplicate")
        if 'archive' in actions and 'is_admin' in roles:
            tmp_actions.append("archive")
        actions = tmp_actions

        # process the request in default view
        if request.method == "GET":
            context = self.context
            context.update({
                'application': application,
                'actions': actions,
                'state': self.name,
                'roles': roles})
            return render_to_response(
                'kgapplications/common_detail.html',
                context,
                context_instance=RequestContext(request))
        elif request.method == "POST":
            for action in actions:
                if action in request.POST:
                    return action

        # we don't know how to handle this request.
        return HttpResponseBadRequest("<h1>Bad Request</h1>")


class Transition(object):
    """ A transition from one state to another. """

    def __init__(self):
        pass

    def get_next_state(self, request, application, roles):
        """ Retrieve the next state. """
        raise NotImplementedError()


def get_application(**kwargs):
    try:
        application = Application.objects.get(**kwargs)
    except Application.DoesNotExist:
        application = None

    try:
        if application is not None:
            application = application.get_object()
            return application
    except Application.DoesNotExist:
        raise RuntimeError("The application is currupt.")

    raise Http404("The application does not exist.")


_types = {}


def setup_application_type(application_type, state_machine):
    _types[application_type] = state_machine


def get_state_machine(application):
    application = application.get_object()
    return _types[type(application)]
