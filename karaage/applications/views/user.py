# Copyright 2007-2010 VPAC
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

""" This file shows the application views using a state machine. """

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail

import datetime
from andsome.forms import EmailForm

from karaage.util.decorators import login_required
from karaage.applications.models import ProjectApplication, Applicant, Application
import karaage.applications.forms as forms
import karaage.applications.emails as emails
import karaage.util.saml as saml
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.institutes.models import Institute
from karaage.util import log_object as log

import json

def _get_url(request, application, auth, label=None):
    """ Retrieve a link that will work for the current user. """
    args = []
    if label is not None:
        args.append(label)

    # don't use secret_token unless we have to
    if auth['is_admin']:
        # Administrators can access anything without secrets
        require_secret = False
    elif not auth['is_applicant']:
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
        person = request.user
        url = reverse(
                'kg_application_detail',
                args=[application.pk, application.state] + args)
    else:
        url = reverse(
                'kg_application_unauthenticated',
                args=[application.secret_token, application.state] + args)
    return url


def _get_email_link(application):
    """ Retrieve a link that can be emailed to the user. """
    # don't use secret_token unless we have to
    if application.content_type.model != 'applicant':
        url = '%s/applications/%d/' % (
                settings.REGISTRATION_BASE_URL, application.pk)
        is_secret = False
    else:
        url = '%s/applications/%s/' % (
                settings.REGISTRATION_BASE_URL, application.secret_token)
        is_secret = True
    return url, is_secret


def _get_applicant_from_saml(request):
    attrs, _ = saml.parse_attributes(request)
    saml_id = attrs['persistent_id']
    try:
        return Person.objects.get(saml_id=saml_id)
    except Person.DoesNotExist:
        pass

    try:
        return Applicant.objects.get(saml_id=saml_id)
    except Applicant.DoesNotExist:
        pass

    return None

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
        if self._first_state is None:
            self._first_state = state_id
        self._states[state_id] = state, actions

    def start(self, request, application, auth_override):
        """ Continue the state machine at first state. """
        # Get the authentication of the current user
        auth = self._authenticate(request, application)
        if auth_override is not None:
            auth.update(auth_override)

        # Ensure current user is authenticated. If user isn't applicant,
        # leader, delegate or admin, they probably shouldn't be here.
        if (not auth['is_applicant'] and
                not auth['is_leader'] and
                not auth['is_delegate'] and
                not auth['is_admin']):
            return HttpResponseForbidden('<h1>Access Denied</h1>')

        # Sanity check
        if self._first_state is None:
            raise RuntimeError("First state not set.")

        # Go to first state.
        return self._next(request, application, auth, self._first_state)

    def process(self, request, application, expected_state, label, auth_override):
        """ Process the view request at the current state. """

        # Get the authentication of the current user
        auth = self._authenticate(request, application)
        if auth_override is not None:
            auth.update(auth_override)

        # Ensure current user is authenticated. If user isn't applicant,
        # leader, delegate or admin, they probably shouldn't be here.
        if (not auth['is_applicant'] and
                not auth['is_leader'] and
                not auth['is_delegate'] and
                not auth['is_admin']):
            return HttpResponseForbidden('<h1>Access Denied</h1>')

        # If user didn't supply state on URL, redirect to full URL.
        if expected_state is None:
            url = _get_url(request, application, auth, label)
            return HttpResponseRedirect(url)

        # Check that the current state is valid.
        if application.state not in self._states:
            raise RuntimeError("Invalid state '%s'" % application.state)

        # If state user expected is different to state we are in, warn user
        # and jump to expected state.
        if expected_state != application.state:
            # post data will be lost
            if request.method == "POST":
                messages.warning(request, "Discarding request and jumping to current state.")
            # note we discard the label, it probably isn't relevant for new
            # state
            url = _get_url(request, application, auth)
            return HttpResponseRedirect(url)

        # Get the current state for this application
        state, actions =  self._states[application.state]

        # Finally do something
        if request.method == "GET":
            # if method is GET, state does not ever change.
            response = state.view(
                    request, application, label, auth, actions.keys())
            assert isinstance(response, HttpResponse)
            return response

        elif request.method == "POST":
            # if method is POST, it can return a HttpResponse or a string
            response = state.view(
                    request, application, label, auth, actions.keys())
            if isinstance(response, HttpResponse):
                # If it returned a HttpResponse, state not changed, just display
                return response
            else:
                # If it returned a string, lookit up in the actions for this
                # state
                if response not in actions:
                    raise RuntimeError(
                            "Invalid response '%s' from state '%s'" %
                            (response, state))
                next_state_key = actions[response]
                # If next state is a transition, process it
                if isinstance(next_state_key, Transition):
                    next_state_key = next_state_key.get_next_state(
                            request, application, auth)
                # Go to the next state
                return self._next(request, application, auth, next_state_key)

        else:
            # Shouldn't happen, user did something weird
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


    ###################
    # PRIVATE METHODS #
    ###################
    @staticmethod
    def _log(request, application, flag, message):
        """ Log a message for this application. """
        log(request.user, application, flag, message)

    @staticmethod
    def _authenticate(request, application):
        """ Check the authentication of the current user. """
        if not request.user.is_authenticated():
            return { 'is_applicant': False, 'is_leader': False, 'is_delegate': False, 'is_admin': False, }
        person = request.user
        auth = application.authenticate(person)
        auth["is_admin"] = False
        return auth

    def _next(self, request, application, auth, state_key):
        """ Continue the state machine at given state. """
        # we only support state changes for POST requests
        if request.method == "POST":
            # lookup next state
            if state_key not in self._states:
                raise RuntimeError("Invalid state '%s'" % self._first_state)
            state, _ = self._states[state_key]

            # enter that state
            state.enter_state(request, application)
            application.state = state_key
            application.save()

            # log details
            self._log(request, application, 2, "state: %s" % state.name)

            # redirect to this new state
            url = _get_url(request, application, auth)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


class State(object):
    """ A abstract class that is the base for all application states. """
    name = "Abstract State"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        pass

    def view(self, request, application, label, auth, actions):
        """ Django view method. We provide a default detail view for
        applications. """

        # We only provide a view for when no label provided
        if label is not None:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # only reopen/reinvite actions make sense for default view
        tmp_actions = []
        if 'reopen' in actions:
            tmp_actions.append("reopen")
        if 'reinvite' in actions:
            tmp_actions.append("reinvite")
        if 'archive' in actions and auth['is_admin']:
            tmp_actions.append("archive")
        actions = tmp_actions

        # process the request in default view
        if request.method == "GET":
            return render_to_response(
                    'applications/application_detail.html',
                    {'application': application,
                    'actions': actions,
                    'state': self.name,
                    'auth': auth},
                    context_instance=RequestContext(request))
        elif request.method == "POST":
            for action in actions:
                if action in request.POST:
                    return action

        # we don't know how to handle this request.
        return HttpResponseBadRequest("<h1>Bad Request</h1>")


class Transition(object):
    """ A transition from one state to another. """
    def __init__(self, next_state_id):
        self._next_state_id = next_state_id

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        return self._next_state_id


class StateWithSteps(State):
    """ A state that has a number of steps to complete. """
    def __init__(self):
        self._first_step = None
        self._steps = {}
        self._order = []
        super(StateWithSteps, self).__init__()

    def add_step(self, step, step_id):
        """ Add a step to the list. The first step added becomes the initial
        step. """
        assert step_id not in self._steps
        assert step_id not in self._order

        self._steps[step_id] = step
        self._order.append(step_id)

    def view(self, request, application, label, auth, actions):
        """ Process the view request at the current step. """

        # if the user is not the applicant, the steps don't apply.
        if not auth['is_applicant'] or auth['is_admin']:
            return super(StateWithSteps, self).view(request, application, label, auth, actions)

        # was label supplied?
        if label is None:
            # no label given, find first step and redirect to it.
            this_id = self._order[0]
            url = _get_url(request, application, auth, this_id)
            return HttpResponseRedirect(url)
        else:
            # label was given, get the step position and id for it
            this_id = label
            if this_id not in self._steps:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
            position = self._order.index(this_id)

        # get the step given the label
        this_step =  self._steps[this_id]

        # define list of allowed actions for step
        step_actions = {}
        if 'cancel' in actions:
            step_actions['cancel'] = "state:cancel"
        if 'submit' in actions and position == len(self._order)-1:
            step_actions['submit'] = "state:submit"
        if position > 0:
            step_actions['prev'] = self._order[position-1]
        if position < len(self._order)-1:
            step_actions['next'] = self._order[position+1]

        # process the request
        if request.method == "GET":
            # if GET request, state changes are not allowed
            response = this_step.view(
                    request, application, this_id, auth, step_actions.keys())
            assert isinstance(response, HttpResponse)
            return response
        elif request.method == "POST":
            # if POST request, state changes are allowed
            response = this_step.view(
                    request, application, this_id, auth, step_actions.keys())
            assert response is not None

            # If it was a HttpResponse, just return it
            if isinstance(response, HttpResponse):
                return response
            else:
                # try to lookup the response
                if response not in step_actions:
                    raise RuntimeError(
                            "Invalid response '%s' from step '%s'" %
                            (response, this_step))
                action = step_actions[response]

                # process the required action
                if action.startswith("state:"):
                    return action[6:]
                else:
                    url = _get_url(request, application, auth, action)
                    return HttpResponseRedirect(url)

        # We only understand GET or POST requests
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # If we get this far, something went wrong.
        assert False


class Step(object):
    """ A single step in a StateWithStep state. """
    def view(self, request, application, label, auth, actions):
        return NotImplementedError()


class StateStepIntroduction(Step):
    """ Invitation has been sent to applicant. """
    name = "Read introduction"

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        application.applicant.email_verified = True
        application.applicant.save()
        for action in actions:
            if action in request.POST:
                return action
        link, is_secret = _get_email_link(application)
        return render_to_response('applications/state_aed_introduction.html',
                {'actions': actions, 'application': application, 'auth': auth,
                'link': link, 'is_secret': is_secret },
                context_instance=RequestContext(request))


class StateStepShibboleth(Step):
    """ Invitation has been sent to applicant. """
    name = "Invitation sent"

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        status = None
        applicant = application.applicant
        attrs = []

        saml_session = saml.is_saml_session(request)

        # certain actions are supported regardless of what else happens
        if 'cancel' in request.POST:
            return "cancel"
        if 'prev' in request.POST:
            return 'prev'

        # test for conditions where shibboleth registration not required
        if applicant.saml_id is not None:
            status = "You have already registered a shibboleth id."
            form = None
            done = True
#        elif application.content_type.model != 'applicant':
#            status = "You are already registered in the system."
#            form = None
#            done = True
        elif (applicant.institute is not None and
                applicant.institute.saml_entityid is None):
            status = "Your institute does not have shibboleth registered."
            form = None
            done = True

        elif Institute.objects.filter(saml_entityid__isnull=False).count() == 0:
            status = "No institutes support shibboleth here."
            form = None
            done = True

        else:
            # shibboleth registration is required

            # Do construct the form
            form = saml.SAMLInstituteForm(request.POST or None,
                    initial = {'institute': applicant.institute})
            done = False
            status = None

            # Was it a POST request?
            if request.method == 'POST':

                # Did the login form get posted?
                if 'login' in request.POST and form.is_valid():
                    institute = form.cleaned_data['institute']
                    applicant.institute = institute
                    applicant.save()
                    # We do not set application.insitute here, that happens
                    # when application, if it is a ProjectApplication, is
                    # submitted

                    # if institute supports shibboleth, redirect back here via
                    # shibboleth, otherwise redirect directly back he.
                    url = _get_url(request, application, auth, label)
                    if institute.saml_entityid is not None:
                        url = saml.build_shib_url(
                                request, url, institute.saml_entityid)
                    return HttpResponseRedirect(url)

                # Did we get a register request?
                elif 'register' in request.POST:
                    if saml_session:
                        applicant = _get_applicant_from_saml(request)
                        if applicant is not None:
                            application.applicant = applicant
                            application.save()
                        else:
                            applicant = application.applicant

                        applicant = saml.add_saml_data(
                                applicant, request)
                        applicant.save()

                        url = _get_url(request, application, auth, label)
                        return HttpResponseRedirect(url)
                    else:
                        return HttpResponseBadRequest("<h1>Bad Request</h1>")

                # Did we get a logout request?
                elif 'logout' in request.POST:
                    if saml_session:
                        url = saml.logout_url(request)
                        return HttpResponseRedirect(url)
                    else:
                        return HttpResponseBadRequest("<h1>Bad Request</h1>")

            # did we get a shib session yet?
            if saml_session:
                attrs, _ = saml.parse_attributes(request)
                saml_session = True


        # if we are done, we can proceed to next state
        if request.method == 'POST':
            if done:
                for action in actions:
                    if action in request.POST:
                        return action
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
            else:
                status = "Please register with Shibboleth before proceeding."

        # render the page
        return render_to_response(
                'applications/state_aed_shibboleth.html',
                {'form': form, 'done': done, 'status': status,
                    'actions': actions, 'auth': auth, 'application': application,
                    'attrs': attrs, 'saml_session': saml_session,},
                context_instance=RequestContext(request))


class StateStepApplicant(Step):
    """ Application is open and user is can edit it."""
    name = "Open"

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        # Get the appropriate form
        status = None
        if application.content_type.model != 'applicant':
            status = "You are already registered in the system."
            form = None
        elif application.content_type.model == 'applicant':
            if application.applicant.saml_id is not None:
                form = forms.SAMLApplicantForm(
                        request.POST or None,
                        instance=application.applicant)
            else:
                form = forms.UserApplicantForm(
                        request.POST or None,
                        instance=application.applicant)

        # Process the form, if there is one
        if form is not None and request.method == 'POST':
            if form.is_valid():
                form.save(commit=True)
                for action in actions:
                    if action in request.POST:
                        return action
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
            else:
                # if form didn't validate and we want to go back or cancel,
                # then just do it.
                if 'cancel' in request.POST:
                    return "cancel"
                if 'prev' in request.POST:
                    return 'prev'


        # If we don't have a form, we can just process the actions here
        if form is None:
            for action in actions:
                if action in request.POST:
                    return action

        # Render the response
        return render_to_response(
                'applications/state_aed_applicant.html', {
                'form': form,
                'application': application,
                'status': status, 'actions': actions, 'auth': auth },
                context_instance=RequestContext(request))


class StateStepProject(State):
    """ Applicant is able to choose the project for the application. """
    name = "Choose project"

    def handle_ajax(self, request, application):
        resp = {}
        if 'leader' in request.POST:
            leader = Person.objects.get(pk=request.POST['leader'])
            project_list = leader.leaders.filter(is_active=True)
            resp['project_list'] = [(p.pk, unicode(p)) for p in project_list]

        elif 'terms' in request.POST:
            terms = request.POST['terms'].lower()
            try:
                project = Project.active.get(pid__icontains=terms)
                resp['project_list'] = [ (project.pk, unicode(project)) ]
            except Project.DoesNotExist:
                resp['project_list'] = []
            except Project.MultipleObjectsReturned:
                resp['project_list'] = []
            leader_list = Person.active.filter(
                institute=application.applicant.institute,
                leaders__is_active=True).distinct()
            if len(terms) >= 3:
                query = Q()
                for term in terms.split(' '):
                    q =     Q(username__icontains=term)
                    q = q | Q(first_name__icontains=term)
                    q = q | Q(last_name__icontains=term)
                    query = query & q
                leader_list = leader_list.filter(query)
                resp['leader_list'] = [(p.pk, "%s (%s)"%(p,p.username)) for p in leader_list]
            else:
                resp['error'] = "Please enter at lease three characters for search."
                resp['leader_list'] = []

        return resp

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if 'ajax' in request.POST:
            resp = self.handle_ajax(request, application)
            return HttpResponse(json.dumps(resp), mimetype="application/json")


        form_models = {
                'common': forms.CommonApplicationForm,
                'new': forms.NewProjectApplicationForm,
                'existing': forms.ExistingProjectApplicationForm,
        }

        project_forms = {}

        for key, form in form_models.iteritems():
            project_forms[key] = form(
                    request.POST or None, instance=application)

        if application.project is not None:
            project_forms["common"].initial = { 'application_type': 'U' }
        elif application.name != "":
            project_forms["common"].initial = { 'application_type': 'P' }

        if 'application_type' in request.POST:
            at = request.POST['application_type']
            valid = True
            if at == 'U':
                # existing project
                if project_forms['common'].is_valid():
                    project_forms['common'].save(commit=False)
                else:
                    valid = False
                if project_forms['existing'].is_valid():
                    project_forms['existing'].save(commit=False)
                else:
                    valid = False

            elif at == 'P':
                # new project
                if project_forms['common'].is_valid():
                    project_forms['common'].save(commit=False)
                else:
                    valid = False
                if project_forms['new'].is_valid():
                    project_forms['new'].save(commit=False)
                else:
                    valid = False
                application.institute = application.applicant.institute

            else:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")

            # reset hidden forms
            if at != 'U':
                # existing project form was not displayed
                project_forms["existing"] = (
                        form_models["existing"](instance=application))
                application.project = None
                application.make_leader = False
            if at != 'P':
                # new project form was not displayed
                project_forms["new"] = form_models["new"](instance=application)
                application.name = ""
                application.institute = None
                application.description = None
                application.additional_req = None
                application.machine_categories = []
                application.pid = None

            # save the values
            application.save()

            if project_forms['new'].is_valid() and at == 'P':
                project_forms["new"].save_m2m()

            # we still need to process cancel and prev even if form were
            # invalid
            if 'cancel' in request.POST:
                return "cancel"
            if 'prev' in request.POST:
                return 'prev'

            # if forms were valid, jump to next state
            if valid:
                for action in actions:
                    if action in request.POST:
                        return action
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
        else:
            # we still need to process cancel, prev even if application type
            # not given
            if 'cancel' in request.POST:
                return "cancel"
            if 'prev' in request.POST:
                return 'prev'

        # lookup the project based on the form data
        project_id = project_forms['existing']['project'].value()
        project = None
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                pass

        # render the response
        return render_to_response(
                'applications/state_aed_project.html',
                {'forms': project_forms, 'project': project,
                    'actions': actions, 'auth': auth, },
                context_instance=RequestContext(request))


class StateApplicantEnteringDetails(StateWithSteps):
    name = "Applicant entering details."

    def __init__(self):
        super(StateApplicantEnteringDetails, self).__init__()
        self.add_step(StateStepIntroduction(), 'intro')
        if settings.SHIB_SUPPORTED:
            self.add_step(StateStepShibboleth(), 'shibboleth')
        self.add_step(StateStepApplicant(), 'applicant')
        self.add_step(StateStepProject(), 'project')

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        application.reopen()
        link, is_secret = _get_email_link(application)
        emails.send_applicant_invite_email(application, link, is_secret)
        messages.success(
                request,
                "Sent an invitation to %s." %
                (application.applicant.email))

    def view(self, request, application, label, auth, actions):
        """ Process the view request at the current step. """

        # if user is logged and and not applicant, steal the
        # application
        if auth['is_applicant']:
            # if we got this far, then we either we are logged in as applicant, or
            # we know the secret for this application.

            new_person = None

            attrs, _ = saml.parse_attributes(request)
            saml_id = attrs['persistent_id']
            try:
                if saml_id is not None:
                    new_person = Person.objects.get(saml_id=saml_id)
                    reason = "SAML id is already in use by existing person."
                    details = ("It is not possible to continue this application " +
                        "as is because the saml identity already exists " +
                        "as a registered user.")
            except Person.DoesNotExist:
                pass

            if request.user.is_authenticated():
                new_person = request.user
                reason = "%s was logged in and accessed secret URL." % new_person
                details = ("If you want to access this application "+
                    "as %s " % application.applicant +
                    "without %s stealing it, " % new_person +
                    "you will have to ensure %s is " % new_person +
                    "logged out first.")

            if new_person is not None:
                if application.applicant != new_person:
                    if 'steal' in request.POST:
                        old_applicant = application.applicant
                        application.applicant = new_person
                        application.save()
                        log(request.user, application,
                                1, "Stolen application from %s", application.applicant)
                        messages.success(
                                request,
                                "Stolen application from %s", application.applicant)
                        url = _get_url(request, application, auth, label)
                        return HttpResponseRedirect(url)
                    else:
                        return render_to_response(
                                'applications/application_steal.html',
                                {'application': application, 'person': new_person,
                                    'reason': reason, 'details': details, },
                                context_instance=RequestContext(request))

        # if the user is the leader, show him the leader specific page.
        if (auth['is_leader'] or auth['is_delegate']) and not auth['is_admin'] and not auth['is_applicant']:
            actions = ['reinvite']
            if 'reinvite' in request.POST:
                return 'reinvite'
            return render_to_response(
                    'applications/state_aed_for_leader.html',
                    {'application': application, 'actions': actions, 'auth': auth, },
                    context_instance=RequestContext(request))

        # otherwise do the default behaviour for StateWithSteps
        return super(StateApplicantEnteringDetails, self).view(request, application, label, auth, actions)


class StateWaitingForApproval(State):
    """ We need the somebody to provide approval. """
    name = "Waiting for X"

    def check_auth(self, auth):
        """ Check the person's authorization. """
        raise NotImplementedError()

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label == "approve" and self.check_auth(auth):
            actions = [ 'approve' ]
            application_form = forms.ApproveApplicationFormGenerator(
                    application, auth)
            form = application_form(
                    request.POST or None, instance=application)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    return "approve"
            return render_to_response(
                    self.template_approve,
                    {'application': application, 'form': form,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        elif label == "decline" and self.check_auth(auth):
            actions = [ 'decline' ]
            if request.method == 'POST':
                form = EmailForm(request.POST)
                if form.is_valid():
                    to_email = application.applicant.email
                    subject, body = form.get_data()
                    emails.send_mail(
                            subject, body,
                            settings.ACCOUNTS_EMAIL, [to_email],
                            fail_silently=False)
                    return "decline"
            else:
                link, is_secret = _get_email_link(application)
                subject, body = emails.render_email(
                        'applicant_declined',
                        {'receiver': application.applicant,
                        'application': application,
                        'link': link, 'is_secret': is_secret })
                initial_data = {'body': body, 'subject': subject}
                form = EmailForm(initial=initial_data)
            return render_to_response(
                    self.template_decline,
                    {'application': application, 'form': form,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateWaitingForApproval, self).view(
                request, application, label, auth, actions)


class StateWaitingForLeader(StateWaitingForApproval):
    """ We need the leader to provide approval. """
    name = "Waiting for leader"
    template_approve = "applications/state_leader_approve_for_leader.html"
    template_decline = "applications/state_leader_decline_for_leader.html"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        assert application.project is not None
        emails.send_leader_request_email(application)

    def check_auth(self, auth):
        """ Check the person's authorization. """
        return auth['is_leader']


class StateWaitingForDelegate(StateWaitingForApproval):
    """ We need the delegate to provide approval. """
    name = "Waiting for delegate"
    template_approve = "applications/state_delegate_approve_for_delegate.html"
    template_decline = "applications/state_delegate_decline_for_delegate.html"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        emails.send_delegate_request_email(application)

    def check_auth(self, auth):
        """ Check the person's authorization. """
        return auth['is_delegate']


class StateWaitingForAdmin(State):
    """ We need the administrator to provide approval. """
    name = "Waiting for administrator"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        emails.send_admin_request_email(application)

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label == "approve" and auth['is_admin']:
            similar_people = []
            if application.content_type.model == 'applicant':
                similar_people = Person.objects.filter(
                        Q(email=application.applicant.email) |
                        Q(username=application.applicant.username) |
                        (Q(full_name__icontains=application.applicant.first_name) &
                        Q(full_name__icontains=application.applicant.last_name))
                )
            actions = [ 'approve' ]
            application_form = forms.AdminApproveApplicationFormGenerator(
                    application, auth)
            form = application_form(
                    request.POST or None, instance=application)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    return "approve"
            return render_to_response(
                    'applications/state_admin_approve_for_admin.html',
                    {'application': application, 'form': form,
                        'actions': actions, 'auth': auth,
                        'similar_people': similar_people, },
                    context_instance=RequestContext(request))
        elif label == "decline" and auth['is_admin']:
            actions = [ 'decline' ]
            if request.method == 'POST':
                form = EmailForm(request.POST)
                if form.is_valid():
                    to_email = application.applicant.email
                    subject, body = form.get_data()
                    emails.send_mail(
                            subject, body,
                            settings.ACCOUNTS_EMAIL, [to_email],
                            fail_silently=False)
                    return "decline"
            else:
                link, is_secret = _get_email_link(application)
                subject, body = emails.render_email(
                        'applicant_declined',
                        {'receiver': application.applicant,
                        'application': application,
                        'link': link, 'is_secret': is_secret})
                initial_data = {'body': body, 'subject': subject}
                form = EmailForm(initial=initial_data)
            return render_to_response(
                    'applications/state_admin_decline_for_admin.html',
                    {'application': application, 'form': form,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateWaitingForAdmin, self).view(
                request, application, label, auth, actions)



class StatePassword(State):
    """ This application is completed and processed. """
    name = "Completed"


    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label is None and auth['is_applicant']:
            assert application.content_type.model == 'person'
            if application.applicant.has_usable_password():
                form = forms.PersonVerifyPassword(data=request.POST or None, person=application.applicant)
                form_type = "verify"
            else:
                form = forms.PersonSetPassword(data=request.POST or None, person=application.applicant)
                form_type = "set"
            if request.method == 'POST':
                for action in actions:
                    if 'cancel' in request.POST:
                        return action
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Password updated. New accounts activated.')
                    for action in actions:
                        if action in request.POST:
                            return action
                    return HttpResponseBadRequest("<h1>Bad Request</h1>")
            return render_to_response(
                    'applications/state_password_for_applicant.html',
                    {'application': application, 'form': form,
                        'actions': actions, 'auth': auth, 'type': form_type },
                    context_instance=RequestContext(request))
        return super(StatePassword, self).view(
                request, application, label, auth, actions)



class StateCompleted(State):
    """ This application is completed and processed. """
    name = "Completed"


class StateArchived(State):
    """ This application is archived. """
    name = "Archived"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        pass

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label is None and auth['is_applicant']:
            return render_to_response(
                    'applications/state_archived.html',
                    {'help_email': settings.ACCOUNTS_EMAIL,
                    'application': application,
                    'actions': actions, 'auth': auth, },
                    context_instance=RequestContext(request))
        return super(StateArchived, self).view(
                request, application, label, auth, actions)


class StateDeclined(State):
    """ This application declined. """
    name = "Declined"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        application.decline()

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label is None and auth['is_applicant']:
            # applicant, admin, leader can reopen an application
            if 'reopen' in request.POST:
                return 'open'
            return render_to_response(
                    'applications/state_declined_for_applicant.html',
                    {'application': application,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateDeclined, self).view(
                request, application, label, auth, actions)


class TransitionSubmit(Transition):
    """ A transition after application submitted. """
    def __init__(self, on_existing_project, on_new_project, on_error):
        self._on_existing_project = on_existing_project
        self._on_new_project = on_new_project
        self._on_error = on_error

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        # Check for serious errors in submission.
        # Should never happen unless user skips steps.
        if application.applicant is None:
            return self._on_error
        if not application.applicant.username:
            return self._on_error
        if not application.applicant.first_name:
            return self._on_error
        if application.project is None:
            if not application.name:
                return self._on_error
            if application.institute is None:
                return self._on_error
        application.submit()

        # Do we need to wait for leader or delegate approval?
        if application.project is None:
            return self._on_new_project
        else:
            return self._on_existing_project


class TransitionApprove(Transition):
    """ A transition after application fully approved. """
    def __init__(self, on_password_needed, on_password_ok):
        self._on_password_needed = on_password_needed
        self._on_password_ok = on_password_ok

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        approved_by = request.user
        created_person, created_account, created_project = application.approve(approved_by)

        if created_project:
            emails.send_project_approved_email(application)

        if created_person or created_account:
            link, is_secret = _get_email_link(application)
            emails.send_applicant_approved_email(
                    application, created_person, created_account, link, is_secret)
            return self._on_password_needed
        else:
            return self._on_password_ok


def get_application_state_machine():
    """ Get the default state machine for applications. """
    state_machine = StateMachine()
    state_machine.add_state(StateApplicantEnteringDetails(), 'O',
            { 'cancel': 'R', 'submit': TransitionSubmit(on_existing_project='L', on_new_project='D', on_error="R"), 'reinvite': 'O', })
    state_machine.add_state(StateWaitingForLeader(), 'L',
            { 'decline': 'R', 'approve': 'K', })
    state_machine.add_state(StateWaitingForDelegate(), 'D',
            { 'decline': 'R', 'approve': 'K', })
    state_machine.add_state(StateWaitingForAdmin(), 'K',
            { 'decline': 'R', 'approve': TransitionApprove(on_password_needed='P', on_password_ok='C')})
    state_machine.add_state(StatePassword(), 'P',
            { 'submit': 'C', })
    state_machine.add_state(StateCompleted(), 'C',
            { 'archive': 'A', })
    state_machine.add_state(StateArchived(), 'A',
            {})
    state_machine.add_state(StateDeclined(), 'R',
            { 'reopen': 'O',  })
#    NEW = 'N'
#    OPEN = 'O'
#    WAITING_FOR_LEADER = 'L'
#    WAITING_FOR_DELEGATE = 'D'
#    WAITING_FOR_ADMIN = 'K'
#    PASSWORD = 'P'
#    COMPLETED = 'C'
#    ARCHIVED = 'A'
#    DECLINED = 'R'
    return state_machine


def get_applicant_from_email(email):
    try:
        applicant = Person.active.get(email=email)
        existing_person = True
    except Person.DoesNotExist:
        applicant, _ = Applicant.objects.get_or_create(email=email)
        existing_person = False
    return applicant, existing_person

def _send_invitation(request, project, invite_form, override_auth):
    """ The logged in project leader OR administrator wants to invite somebody.
    """
    form = invite_form(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():

            email = form.cleaned_data['email']
            applicant, existing_person = get_applicant_from_email(email)

            if existing_person and not 'existing' in request.POST:
                return render_to_response(
                        'applications/application_invite_existing.html',
                        {'form': form, 'person': applicant},
                        context_instance=RequestContext(request))

            application = form.save(commit=False)
            application.applicant = applicant
            if project is not None:
                application.project = project
            application.save()
            state_machine = get_application_state_machine()
            response = state_machine.start(request, application, override_auth)
            return response

    return render_to_response(
            'applications/application_invite_unauthenticated.html',
            {'form': form, 'project': project, },
            context_instance=RequestContext(request))


@login_required
def send_invitation(request, project_id):
    """ The logged in project leader wants to invite somebody to their project.
    """

    person = request.user
    project = get_object_or_404(Project, pk=project_id)

    if person not in project.leaders.all():
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    override_auth = { 'is_leader': True }
    return _send_invitation(request, project,
            forms.InviteUserApplicationForm, override_auth)


@login_required
def admin_send_invitation(request, project_id=None):
    """ The logged in administrator wants to invite somebody to their project.
    """
    project_id = None
    if project_id is not None:
        project = get_object_or_404(Project, pk=project_id)

    override_auth = { 'is_admin': True }
    return _send_invitation(request, project_id,
            forms.AdminInviteUserApplicationForm, override_auth)


def new_application(request):
    """ A new application by a user to start a new project. """
    # Note default applications/index.html will display error if user logged in.
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response('applications/application_disabled.html', {}, context_instance=RequestContext(request))

    if not request.user.is_authenticated():
        form = forms.UnauthenticatedInviteUserApplicationForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                email = form.cleaned_data['email']
                applicant, existing_person = get_applicant_from_email(email)
                assert not existing_person

                application = ProjectApplication()
                application.applicant = applicant
                application.save()

                state_machine = get_application_state_machine()
                state_machine.start(request, application, { 'is_applicant': True })
                # we do not show unauthenticated users the application at this stage.
                url = reverse('index')
                return HttpResponseRedirect(url)
        return render_to_response(
                'applications/application_invite_unauthenticated.html',
                {'form': form, },
                context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
                person = request.user

                application = ProjectApplication()
                application.applicant = person
                application.save()

                state_machine = get_application_state_machine()
                response = state_machine.start(request, application, { 'is_applicant': True })
                return response
        return render_to_response(
                'applications/application_invite_authenticated.html',
                {},
                context_instance=RequestContext(request))


@login_required
def index(request):
    """ A logged in project leader or institute delegate wants to see all his
    pending applications. """
    return render_to_response(
            'applications/index.html',
            {},
            context_instance=RequestContext(request))

@login_required
def pending_applications(request):
    """ A logged in project leader or institute delegate wants to see all his
    pending applications. """
    person = request.user
    my_applications = ProjectApplication.objects.filter(
            applicant=person).exclude(
            state__in=[Application.COMPLETED, Application.ARCHIVED, Application.DECLINED])

    query = Q(project__in=person.leaders.all(), state=Application.WAITING_FOR_LEADER)
    query = query | Q(institute__in=person.delegate.all(), state=Application.WAITING_FOR_DELEGATE)

    user_applications = ProjectApplication.objects.filter(query, project__isnull=False)
    project_applications = ProjectApplication.objects.filter(query, project__isnull=True)

    return render_to_response(
            'applications/application_list.html',
            {
            'my_applications': my_applications,
            'user_applications': user_applications,
            'project_applications': project_applications},
            context_instance=RequestContext(request))


def _get_application(**kwargs):
    try:
        application = ProjectApplication.objects.get(**kwargs)
    except ProjectApplication.DoesNotExist:
        application = None

    if application is not None:
        return application

    raise Http404()

@login_required
def application_detail(request, application_id, state=None, label=None):
    """ An authenticated user is trying to access an application. """
    application = _get_application(pk=application_id)
    state_machine = get_application_state_machine()
    return state_machine.process(request, application, state, label, {})

def application_detail_admin(request, application_id, state=None, label=None):
    """ An authenticated user is trying to access an application. """
    application = _get_application(pk=application_id)
    state_machine = get_application_state_machine()
    return state_machine.process(request, application, state, label, { 'is_admin': True })


def application_unauthenticated(request, token, state=None, label=None):
    """ An unauthenticated user is trying to access an application. """
    application = _get_application(
                secret_token=token, expires__gt=datetime.datetime.now())

    # redirect user to real url if possible.
    if request.user.is_authenticated():
        if request.user == application.applicant:
            url = _get_url(request, application, {'is_applicant': True}, label)
            return HttpResponseRedirect(url)

    state_machine = get_application_state_machine()
    return state_machine.process(request, application, state, label,
            { 'is_applicant': True })
