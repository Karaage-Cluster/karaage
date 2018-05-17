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

""" This file implements a state machine for the views. """
import importlib

from django.conf import settings
from django.contrib import messages
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse

import karaage.common as common
from karaage.common import log

from ..models import Application


def load_state_instance(config):
    assert config['type'] == 'state'
    name = config['class']
    module_name, class_name = name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    klass = getattr(module, class_name)
    assert issubclass(klass, State)
    return klass(config)


def load_transition_instance(config):
    assert config['type'] == 'transition'
    name = config['class']
    module_name, class_name = name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    klass = getattr(module, class_name)
    assert issubclass(klass, Transition)
    return klass(config)


def load_instance(config):
    if config['type'] == 'state':
        return load_state_instance(config)
    if config['type'] == 'transition':
        return load_transition_instance(config)
    else:
        assert False


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
    elif not request.user.is_authenticated:
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

    def __init__(self, config):
        self._first_state = {
            'type': 'goto',
            'key': 'start',
        }
        self._config = config
        super(StateMachine, self).__init__()

    def get_state(self, application):
        if application.state not in self._config:
            raise RuntimeError("Invalid state '%s'" % application.state)
        config = self._config[application.state]
        instance = load_state_instance(config)
        return instance

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
        if application.state not in self._config:
            raise RuntimeError("Invalid current state '%s'" % application.state)

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
        state_config = self._config[application.state]

        # Finally do something
        instance = load_state_instance(state_config)
        if request.method == "GET":
            # if method is GET, state does not ever change.
            response = instance.get_next_config(request, application, label, roles)
            assert isinstance(response, HttpResponse)
            return response

        elif request.method == "POST":
            # if method is POST, it can return a HttpResponse or a string
            response = instance.get_next_config(request, application, label, roles)
            if isinstance(response, HttpResponse):
                # If it returned a HttpResponse, state not changed, just
                # display
                return response
            else:
                # If it returned a string, lookit up in the actions for this
                # state
                next_config = response
                # Go to the next state
                return self._next(request, application, roles, next_config)

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

    def _next(self, request, application, roles, next_config):
        """ Continue the state machine at given state. """
        # we only support state changes for POST requests
        if request.method == "POST":
            key = None

            # If next state is a transition, process it
            while True:
                # We do not expect to get a direct state transition here.
                assert next_config['type'] in ['goto', 'transition']

                while next_config['type'] == 'goto':
                    key = next_config['key']
                    next_config = self._config[key]

                instance = load_instance(next_config)

                if not isinstance(instance, Transition):
                    break

                next_config = instance.get_next_config(request, application, roles)

            # lookup next state
            assert key is not None
            state_key = key

            # enter that state
            instance.enter_state(request, application)
            application.state = state_key
            application.save()

            # log details
            log.change(application.application_ptr, "state: %s" % instance.name)

            # redirect to this new state
            url = get_url(request, application, roles)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


class State(object):
    """ A abstract class that is the base for all application states. """
    name = "Abstract State"
    actions = set()

    def __init__(self, config):
        self.context = {}
        self._config = config
        for action_key in self.actions:
            key = 'on_%s' % action_key
            assert key in config
        actions = self.actions
        for key, value in config.items():
            if key.startswith('on_'):
                action_key = key[3:]
                assert action_key in actions

    def get_actions(self, request, application, roles):
        return self.actions

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        pass

    def get_next_config(self, request, application, label, roles):
        response = self.get_next_action(request, application, label, roles)
        if isinstance(response, HttpResponse):
            return response
        assert response in self.get_actions(request, application, roles)
        key = 'on_%s' % response
        return self._config[key]

    def get_next_action(self, request, application, label, roles):
        """ Django view method. We provide a default detail view for
        applications. """

        # We only provide a view for when no label provided
        if label is not None:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # only certain actions make sense for default view
        actions = self.get_actions(request, application, roles)

        # process the request in default view
        if request.method == "GET":
            context = self.context
            context.update({
                'application': application,
                'actions': actions,
                'state': self.name,
                'roles': roles})
            return render(
                template_name='kgapplications/common_detail.html',
                context=context,
                request=request)
        elif request.method == "POST":
            for action in actions:
                if action in request.POST:
                    return action

        # we don't know how to handle this request.
        return HttpResponseBadRequest("<h1>Bad Request</h1>")


class Transition(object):
    """ A transition from one state to another. """
    actions = set()

    def __init__(self, config):
        self._config = config
        for action in self.actions:
            key = 'on_%s' % action
            assert key in config

    def get_actions(self, request, application, roles):
        return self.actions

    def get_next_config(self, request, application, roles):
        action = self.get_next_action(request, application, roles)
        assert action in self.get_actions(request, application, roles)
        key = 'on_%s' % action
        return self._config[key]

    def get_next_action(self, request, application, roles):
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
        raise RuntimeError("The application is corrupt.")

    raise Http404("The application does not exist.")


_types = {}


def setup_application_type(application_type, state_machine):
    _types[application_type] = state_machine


def get_state_machine(application):
    application = application.get_object()
    return _types[type(application)]
