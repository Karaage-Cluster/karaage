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
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail

import datetime
from django_shibboleth.utils import ensure_shib_session, build_shib_url
from andsome.forms import EmailForm

from karaage.applications.models import UserApplication, ProjectApplication, Applicant, Application
from karaage.applications.forms import UserApplicationForm, ProjectApplicationForm
from karaage.applications.forms import UserApplicantForm, StartApplicationForm, InstituteForm
from karaage.applications.forms import ApproveUserApplicationForm, LeaderApproveProjectApplicationForm, AdminApproveProjectApplicationForm
from karaage.applications.forms import LeaderInviteUserApplicationForm, AdminInviteUserApplicationForm, UnauthenticatedInviteUserApplicationForm
from karaage.applications.forms import PersonSetPassword, PersonVerifyPassword
from karaage.applications.emails import send_account_request_email, send_project_request_email
from karaage.applications.emails import send_account_approved_email, send_project_approved_email
from karaage.applications.emails import send_user_invite_email, send_notify_admin, render_email
from karaage.applications.saml import SAMLApplicantForm, get_saml_user, add_saml_data
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.util import log_object as log

def _get_url(request, application, label=None):
    """ Retrieve a link that will work for the current user. """
    args = []
    if label is not None:
        args.append(label)

    # don't use secret_token unless we have to
    if request.user.is_authenticated():
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
    else:
        url = '%s/applications/%s/' % (
                settings.REGISTRATION_BASE_URL, application.secret_token)
    return url

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

    def start(self, request, application):
        """ Continue the state machine at first state. """
        if self._first_state is None:
            raise RuntimeError("First state not set.")
        return self._next(request, application, self._first_state)

    def process(self, request, application, expected_state, label, auth_override):
        """ Process the view request at the current state. """
        if application.state not in self._states:
            raise RuntimeError("Invalid state '%s'" % application.state)

        # If user didn't supply state on URL, redirect to full URL.
        if expected_state is None:
            url = _get_url(request, application, label)
            return HttpResponseRedirect(url)

        # If state user expected is different to state we are in, warn user
        # and jump to expected state.
        if expected_state != application.state:
            messages.warning(request, "Jumping to current state.")
            url = _get_url(request, application, label)
            return HttpResponseRedirect(url)

        # Get the current state for this application
        state, actions =  self._states[application.state]

        # Get the authentication of the current user
        auth = self._authenticate(request, application)
        if auth_override is not None:
            auth.update(auth_override)

        # Ensure current user is authenticated. If user isn't applicant, leader
        # or admin, they probably shouldn't be here.
        if (not auth['is_applicant'] and
                not auth['is_leader'] and
                not auth['is_admin']):
            return HttpResponseForbidden('<h1>Access Denied</h1>')

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
                return self._next(request, application, next_state_key)
        else:
            # Shouldn't happen
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


    ###################
    # PRIVATE METHODS #
    ###################
    @staticmethod
    def _log(request, application, flag, message):
        """ Log a message for this application. """
        log(request.user, application.application_ptr, flag, message)

    @staticmethod
    def _authenticate(request, application):
        """ Check the authentication of the current user. """
        if not request.user.is_authenticated():
            return { 'is_applicant': False, 'is_leader': False, 'is_admin': False, }
        person = request.user.get_profile()
        auth = application.authenticate(person)
        auth["is_admin"] = False
        return auth

    def _next(self, request, application, state_key):
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
            url = _get_url(request, application)
            return HttpResponseRedirect(url)
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")


class State(object):
    """ A abstract class that is the base for all application states. """
    name = "Abstract State"

    def enter_state(self, request, application):
        """ This is becomming the new current state. """
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
#            delete
#            url = _get_url(request, application)
#            return HttpResponseRedirect(url)

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
        if not auth['is_applicant']:
            return super(StateWithSteps, self).view(request, application, label, auth, actions)

        # was label supplied?
        if label is None:
            # no label given, find first step and redirect to it.
            this_id = self._order[0]
            url = _get_url(request, application, this_id)
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
        actions = {}
        actions['cancel'] = "state:cancel"
        if position > 0:
            actions['prev'] = self._order[position-1]
        if position < len(self._order)-1:
            actions['next'] = self._order[position+1]
        if position == len(self._order)-1:
            actions['submit'] = "state:submit"

        # process the request
        if request.method == "GET":
            # if GET request, state changes are not allowed
            response = this_step.view(
                    request, application, this_id, auth, actions.keys())
            assert isinstance(response, HttpResponse)
            return response
        elif request.method == "POST":
            # if POST request, state changes are allowed
            response = this_step.view(
                    request, application, this_id, auth, actions.keys())
            assert response is not None

            # If it was a HttpResponse, just return it
            if isinstance(response, HttpResponse):
                return response
            else:
                # try to lookup the response
                if response not in actions:
                    raise RuntimeError(
                            "Invalid response '%s' from step '%s'" %
                            (response, this_step))
                action = actions[response]

                # process the required action
                if action.startswith("state:"):
                    return action[6:]
                else:
                    url = _get_url(request, application, action)
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
        link = _get_email_link(application)
        return render_to_response('applications/state_aed_introduction.html',
                {'actions': actions, 'application': application, 'auth': auth, 'link': link },
                context_instance=RequestContext(request))


class StateStepShibboleth(Step):
    """ Invitation has been sent to applicant. """
    name = "Invitation sent"

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        status = None
        applicant = application.applicant

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

        else:
            # shibboleth registration is required

            # Do construct the form
            form = InstituteForm(request.POST or None)
            done = False
            status = None

            # Was it a GET request?
            if request.method == 'GET':
                # did we get a shib session yet?
                response = ensure_shib_session(request)
                if response is None:
                    applicant = add_saml_data(
                            applicant, request)
                    applicant.save()
                    messages.success(
                            request,
                            "Shibboleth has been registered.")
                    done = True

            # Was it a POST request?
            elif request.method == 'POST':

                # Did the form get posted?
                if 'shibboleth' in request.POST and form.is_valid():
                    institute = form.cleaned_data['institute']
                    applicant.institute = institute
                    applicant.email_verified = True
                    applicant.save()
                    # We do not set application.insitute here, that happens
                    # when application, if it is a ProjectApplication, is
                    # submitted

                    # if institute supports shibboleth, redirect back here via
                    # shibboleth, otherwise redirect directly back he.
                    url = _get_url(request, application)
                    if institute.saml_entityid is not None:
                        url = build_shib_url(
                                request, url, institute.saml_entityid)
                    return HttpResponseRedirect(url)

        # if we are done, we can proceed to next state
        if request.method == 'POST' and 'shibboleth' not in request.POST:
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
                'actions': actions, 'auth': auth},
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
                form = SAMLApplicantForm(
                        request.POST or None,
                        instance=application.applicant)
            else:
                form = UserApplicantForm(
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
                'saml': application.applicant.saml_id is not None,
                'status': status, 'actions': actions, 'auth': auth },
                context_instance=RequestContext(request))


class StateStepProject(State):
    """ Applicant is able to choose the project for the application. """
    name = "Choose project"

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        institute = application.applicant.institute
        term_error = leader_list = project_error = None
        q_project = leader = None
        project = application.project
        terms = ""
        project_list = None
        qs = request.META['QUERY_STRING']

        if isinstance(application, UserApplication):
            application_form = UserApplicationForm
            choose_project = True
        elif isinstance(application, ProjectApplication):
            application_form = ProjectApplicationForm
            choose_project = False
        else:
            raise RuntimeError("Unknown application type")

        form = application_form(request.POST or None, instance=application)
        if choose_project:
            # User can choose project
            sel_project = application.project
            if request.method == 'POST':
                if 'cancel' in request.POST:
                    return 'cancel'
                if 'prev' in request.POST:
                    return 'prev'
                if 'project' in request.POST:
                    if form.is_valid():
                        sel_project = Project.objects.get(pk=request.POST['project'])
                        if application.applicant in sel_project.group.members.all():
                            project_error = "You are already a member of the project %s" % sel_project.pid
                        else:
                            application = form.save(commit=False)
                            application.project = sel_project
                            application.save()
                            for action in actions:
                                if action in request.POST:
                                    return action
                            return HttpResponseBadRequest("<h1>Bad Request</h1>")
                    else:
                        sel_project = Project.objects.get(pk=request.POST['project'])
                else:
                    project_error = "You must select a project"

            if 'leader_q' in request.REQUEST:
                terms = request.REQUEST['leader_q'].lower()
                q_project = None
                try:
                    q_project = Project.active.get(pid__icontains=terms)
                except Project.DoesNotExist:
                    pass
                except Project.MultipleObjectsReturned:
                    pass
                leader_list = Person.active.filter(institute=institute, leaders__is_active=True).distinct()
                if len(terms) >= 3:
                    query = Q()
                    for term in terms.split(' '):
                        q =     Q(user__username__icontains=term)
                        q = q | Q(user__first_name__icontains=term)
                        q = q | Q(user__last_name__icontains=term)
                        query = query & q
                    leader_list = leader_list.filter(query)
                    if leader_list.count() == 1:
                        leader = leader_list[0]
                        project_list = leader.leaders.filter(is_active=True)
                        leader_list = None
                    elif leader_list.count() == 0 and not q_project:
                        term_error = "No projects found."
                else:
                    if request.method == 'GET':
                        term_error = "Please enter at lease three characters for search."
                    leader_list = None

            if 'leader' in request.REQUEST:
                leader = Person.objects.get(pk=request.REQUEST['leader'])
                project_list = leader.leaders.filter(is_active=True)
                q_project = None

            if project_list is not None:
                if project_list.count() == 1:
                    project = project_list[0]
                    project_list = None
        else:
            # User cannot pick projects
            sel_project = None
            if request.method == 'POST':
                if form.is_valid():
                    form.save(commit=True)
                    for action in actions:
                        if action in request.POST:
                            return action
                    return HttpResponseBadRequest("<h1>Bad Request</h1>")
                else:
                    if 'cancel' in request.POST:
                        return 'cancel'
                    if 'prev' in request.POST:
                        return 'prev'

        return render_to_response(
            'applications/state_aed_project.html',
            {'term_error': term_error, 'terms': terms,
             'leader_list': leader_list, 'project_error': project_error,
             'project_list': project_list, 'project': project, 'q_project': q_project,
             'sel_project': sel_project, 'choose_project': choose_project,
             'qs': qs, 'form': form, 'actions': actions,
             'leader': leader, 'application': application,
             'needs_account': application.needs_account,
             'auth': auth },
            context_instance=RequestContext(request))


class StateApplicantEnteringDetails(StateWithSteps):

    def __init__(self):
        super(StateApplicantEnteringDetails, self).__init__()
        self.add_step(StateStepIntroduction(), 'intro')
        if settings.SHIB_SUPPORTED:
            self.add_step(StateStepShibboleth(), 'shibboleth')
        self.add_step(StateStepApplicant(), 'applicant')
        self.add_step(StateStepProject(), 'project')

    def enter_state(self, request, application):
        """ This is becomming the new current state. """
        send_user_invite_email(application)
        messages.success(
                request,
                "%s sent an invitation." %
                (application.applicant.email))
        application.reopen()

    def view(self, request, application, label, auth, actions):
        """ Process the view request at the current step. """
        # if the user is the leader, show him the leader specific page.
        if auth['is_leader'] and not auth['is_admin']:
            actions = ['reinvite']
            if 'reinvite' in request.POST:
                return 'reinvite'
            return render_to_response(
                    'applications/state_aed_for_leader.html',
                    {'application': application, 'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))

        # otherwise do the default behaviour for StateWithSteps
        return super(StateApplicantEnteringDetails, self).view(request, application, label, auth, actions)


class StateWaitingForLeader(State):
    """ We need the leader to provide approval. """
    name = "Waiting for leader"

    def enter_state(self, request, application):
        """ This is becomming the new current state. """
        if isinstance(application, UserApplication):
            send_account_request_email(application)
        elif isinstance(application, ProjectApplication):
            send_project_request_email(application)
        else:
            raise RuntimeError("Unknown application type.")

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label == "approve" and auth['is_leader']:
            actions = [ 'approve' ]
            if isinstance(application, UserApplication):
                application_form = ApproveUserApplicationForm
            elif isinstance(application, ProjectApplication):
                application_form = LeaderApproveProjectApplicationForm
            else:
                raise RuntimeError("Unknown application type.")
            form = application_form(
                    request.POST or None, instance=application)
            if request.method == 'POST':
                if form.is_valid():
                    application = form.save()
                    return "approve"
            return render_to_response(
                    'applications/state_leader_approve_for_leader.html',
                    {'application': application, 'form': form,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        elif label == "decline" and auth['is_leader']:
            actions = [ 'decline' ]
            if request.method == 'POST':
                form = EmailForm(request.POST)
                if form.is_valid():
                    to_email = application.applicant.email
                    subject, body = form.get_data()
                    send_mail(
                            subject, body,
                            settings.ACCOUNTS_EMAIL, [to_email],
                            fail_silently=False)
                    return "decline"
            else:
                link = _get_email_link(application)
                subject, body = render_email(
                        'account_declined',
                        {'receiver': application.applicant,
                        'application': application,
                        'link': link})
                initial_data = {'body': body, 'subject': subject}
                form = EmailForm(initial=initial_data)
            return render_to_response(
                    'applications/state_leader_decline_for_leader.html',
                    {'application': application, 'form': form,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateWaitingForLeader, self).view(
                request, application, label, auth, actions)


class StateWaitingForAdmin(State):
    """ We need the administrator to provide approval. """
    name = "Waiting for administrator"

    def enter_state(self, request, application):
        """ This is becomming the new current state. """
        send_notify_admin(application)

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label == "approve" and auth['is_admin']:
            similar_people = []
            if application.content_type.model == 'applicant':
                similar_people = Person.objects.filter(
                        Q(user__email=application.applicant.email) |
                        Q(user__username=application.applicant.username) |
                        (Q(user__first_name=application.applicant.first_name) &
                        Q(user__last_name=application.applicant.last_name))
                )
            actions = [ 'approve' ]
            if isinstance(application, UserApplication):
                application_form = ApproveUserApplicationForm
            elif isinstance(application, ProjectApplication):
                application_form = AdminApproveProjectApplicationForm
            else:
                raise RuntimeError("Unknown application type.")
            form = application_form(
                    request.POST or None, instance=application)
            if request.method == 'POST':
                if form.is_valid():
                    application = form.save()
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
                    send_mail(
                            subject, body,
                            settings.ACCOUNTS_EMAIL, [to_email],
                            fail_silently=False)
                    return "decline"
            else:
                link = _get_email_link(application)
                subject, body = render_email(
                        'account_declined',
                        {'receiver': application.applicant,
                        'application': application,
                        'link': link})
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
            if application.applicant.user.has_usable_password():
                form = PersonVerifyPassword(data=request.POST or None, person=application.applicant)
                form_type = "verify"
            else:
                form = PersonSetPassword(data=request.POST or None, person=application.applicant)
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
        """ This is becomming the new current state. """
        pass

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        return render_to_response(
                'applications/old_userapplication.html',
                {'help_email': settings.ACCOUNTS_EMAIL},
                context_instance=RequestContext(request))


class StateDeclined(State):
    """ This application declined. """
    name = "Declined"

    def enter_state(self, request, application):
        """ This is becomming the new current state. """
        application.decline()

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label is None and auth['is_applicant']:
            # applicant, admin, leader can reopen an application
            for action in actions:
                if 'reopen' in request.POST:
                    return action
            return render_to_response(
                    'applications/state_declined_for_applicant.html',
                    {'application': application,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateDeclined, self).view(
                request, application, label, auth, actions)


class TransitionSubmit(Transition):
    """ A transition after application submitted. """
    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        application.submit()
        return super(TransitionSubmit, self).get_next_state(
                request, application, auth)


class TransitionApprove(Transition):
    """ A transition after application fully approved. """
    def __init__(self, state_password_id, skip_password_id):
        self._state_password_id = state_password_id
        self._skip_password_id = skip_password_id

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        created_person, created_account = application.approve()

        if isinstance(application, UserApplication):
            pass
        elif isinstance(application, ProjectApplication):
            send_project_approved_email(application)
        else:
            raise RuntimeError("Unknown application type.")

        if created_person or created_account:
            link = _get_email_link(application)
            send_account_approved_email(
                    application, created_person, created_account, link)
            return self._state_password_id
        else:
            return self._skip_password_id


def get_application_state_machine():
    """ Get the default state machine for applications. """
    state_machine = StateMachine()
    state_machine.add_state(StateApplicantEnteringDetails(), 'O',
            { 'cancel': 'R', 'submit': TransitionSubmit('L'), 'reinvite': 'O', })
    state_machine.add_state(StateWaitingForLeader(), 'L',
            { 'decline': 'R', 'approve': 'K', })
    state_machine.add_state(StateWaitingForAdmin(), 'K',
            { 'decline': 'R', 'approve': TransitionApprove('P', 'C')})
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
        applicant = Person.active.get(user__email=email)
        existing_person = True
    except Person.DoesNotExist:
        applicant, _ = Applicant.objects.get_or_create(email=email)
        existing_person = False
    return applicant, existing_person

def _send_invitation(request, project_id, invite_form):
    """ The logged in project leader wants to invite somebody to their project.
    """
    project = None
    if project_id is not None:
        project = get_object_or_404(Project, pk=project_id)

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
            response = state_machine.start(request, application)
            return response

    return render_to_response(
            'applications/application_invite_unauthenticated.html',
            {'form': form, 'project': project, 'type': 'user'},
            context_instance=RequestContext(request))


@login_required
def leader_send_invitation(request, project_id):
    return _send_invitation(request, project_id, LeaderInviteUserApplicationForm)


@login_required
def admin_send_invitation(request, project_id=None):
    return _send_invitation(request, project_id, AdminInviteUserApplicationForm)


def new_application(request):
    """ An anonymous or authenticated user has applied for an application for a
    new account or a new project. """
    # Note default applications/index.html will display error if user logged in.
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response('applications/application_disabled.html', {}, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = StartApplicationForm(request.POST)
        if form.is_valid():
            app_type = form.cleaned_data['application_type']
            if app_type == 'U':
                return HttpResponseRedirect(reverse('kg_application_new_user'))
            elif app_type == 'P':
                return HttpResponseRedirect(reverse('kg_application_new_project'))
    else:
        form = StartApplicationForm()

    return render_to_response('applications/application_new.html', {'form': form}, context_instance=RequestContext(request))


def new_userapplication(request):
    """ A new application by a user to join a project. """
    # Note default applications/index.html will display error if user logged in.
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response('applications/application_disabled.html', {}, context_instance=RequestContext(request))

    if not request.user.is_authenticated():
        form = UnauthenticatedInviteUserApplicationForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                email = form.cleaned_data['email']
                applicant, existing_person = get_applicant_from_email(email)
                if existing_person:
                    assert not applicant.is_active

                application = UserApplication()
                application.applicant = applicant
                application.save()

                state_machine = get_application_state_machine()
                response = state_machine.start(request, application)
                return response
        return render_to_response(
                'applications/application_invite_unauthenticated.html',
                {'form': form, 'type': 'user', },
                context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
                person = request.user.get_profile()

                application = UserApplication()
                application.applicant = person
                application.save()

                state_machine = get_application_state_machine()
                response = state_machine.start(request, application)
                return response
        return render_to_response(
                'applications/application_invite_authenticated.html',
                {'type': 'user', },
                context_instance=RequestContext(request))



def new_projectapplication(request):
    """ A new application by a user to start a new project. """
    # Note default applications/index.html will display error if user logged in.
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response('applications/application_disabled.html', {}, context_instance=RequestContext(request))

    if not request.user.is_authenticated():
        form = UnauthenticatedInviteUserApplicationForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                email = form.cleaned_data['email']
                applicant, existing_person = get_applicant_from_email(email)
                assert not existing_person

                application = ProjectApplication()
                application.applicant = applicant
                application.save()

                state_machine = get_application_state_machine()
                response = state_machine.start(request, application)
                return response
        return render_to_response(
                'applications/application_invite_unauthenticated.html',
                {'form': form, 'type': 'project', },
                context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
                person = request.user.get_profile()

                application = ProjectApplication()
                application.applicant = person
                application.save()

                state_machine = get_application_state_machine()
                response = state_machine.start(request, application)
                return response
        return render_to_response(
                'applications/application_invite_authenticated.html',
                {'type': 'project', },
                context_instance=RequestContext(request))


@login_required
def index(request):
    """ A logged in project leader or institute delegate wants to see all his
    pending applications. """
    person = request.user.get_profile()
    my_applications = Application.objects.filter(applicant=person)

    return render_to_response(
            'applications/index.html',
            {'my_applications': my_applications},
            context_instance=RequestContext(request))

@login_required
def pending_applications(request):
    """ A logged in project leader or institute delegate wants to see all his
    pending applications. """
    person = request.user.get_profile()
    my_applications = Application.objects.filter(
            applicant=person).exclude(
            state__in=[Application.COMPLETED, Application.ARCHIVED, Application.DECLINED])
    user_applications = UserApplication.objects.filter(project__in=person.leaders.all(),
            state=Application.WAITING_FOR_LEADER)
    project_applications = ProjectApplication.objects.filter(institute__in=person.delegate.all(),
            state=Application.WAITING_FOR_LEADER)

    return render_to_response(
            'applications/application_list_for_leader.html',
            {
            'my_applications': my_applications,
            'user_applications': user_applications,
            'project_applications': project_applications},
            context_instance=RequestContext(request))


def _get_application(**kwargs):
    try:
        application = UserApplication.objects.get(**kwargs)
    except UserApplication.DoesNotExist:
        application = None

    if application is not None:
        return application

    try:
        if application is None:
            application = ProjectApplication.objects.get(**kwargs)
    except ProjectApplication.DoesNotExist:
        application = None

    if application is not None:
        return application

    raise RuntimeError("oops", kwargs)
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

    # an authenticated user shouldn't be here, but ok if they are the
    # applicant.
    if request.user.is_authenticated():
        if request.user.get_profile() != application.applicant:
            return HttpResponseRedirect(reverse('kg_user_profile'))
        url = _get_url(request, application, label)
        return HttpResponseRedirect(url)

    state_machine = get_application_state_machine()
    return state_machine.process(request, application, state, label,
            { 'is_applicant': True })
