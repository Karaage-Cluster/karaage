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

""" This file shows the project application views using a state machine. """

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

from karaage.common.decorators import login_required
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.institutes.models import Institute
from karaage.common import log, is_admin, saml

import json
import six

from ..models import ProjectApplication, Applicant
from .. import forms, emails
from . import base, states


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


class StateWithSteps(base.State):

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

    def view(self, request, application, label, roles, actions):
        """ Process the view request at the current step. """

        # if the user is not the applicant, the steps don't apply.
        if 'is_applicant' not in roles:
            return super(StateWithSteps, self).view(
                request, application, label, roles, actions)

        # was label supplied?
        if label is None:
            # no label given, find first step and redirect to it.
            this_id = self._order[0]
            url = base.get_url(request, application, roles, this_id)
            return HttpResponseRedirect(url)
        else:
            # label was given, get the step position and id for it
            this_id = label
            if this_id not in self._steps:
                return HttpResponseBadRequest("<h1>Bad Request</h1>")
            position = self._order.index(this_id)

        # get the step given the label
        this_step = self._steps[this_id]

        # define list of allowed actions for step
        step_actions = {}
        if 'cancel' in actions:
            step_actions['cancel'] = "state:cancel"
        if 'submit' in actions and position == len(self._order) - 1:
            step_actions['submit'] = "state:submit"
        if position > 0:
            step_actions['prev'] = self._order[position - 1]
        if position < len(self._order) - 1:
            step_actions['next'] = self._order[position + 1]

        # process the request
        if request.method == "GET":
            # if GET request, state changes are not allowed
            response = this_step.view(
                request, application, this_id, roles, step_actions.keys())
            assert isinstance(response, HttpResponse)
            return response
        elif request.method == "POST":
            # if POST request, state changes are allowed
            response = this_step.view(
                request, application, this_id, roles, step_actions.keys())
            assert response is not None

            # If it was a HttpResponse, just return it
            if isinstance(response, HttpResponse):
                return response
            else:
                # try to lookup the response
                if response not in step_actions:
                    raise RuntimeError(
                        "Invalid response '%s' from step '%s'"
                        % (response, this_step))
                action = step_actions[response]

                # process the required action
                if action.startswith("state:"):
                    return action[6:]
                else:
                    url = base.get_url(request, application, roles, action)
                    return HttpResponseRedirect(url)

        # We only understand GET or POST requests
        else:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # If we get this far, something went wrong.
        assert False


class Step(object):

    """ A single step in a StateWithStep state. """

    def view(self, request, application, label, roles, actions):
        return NotImplementedError()


class StateStepIntroduction(Step):

    """ Invitation has been sent to applicant. """
    name = "Read introduction"

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if application.content_type.model == 'applicant':
            if not application.applicant.email_verified:
                application.applicant.email_verified = True
                application.applicant.save()
        for action in actions:
            if action in request.POST:
                return action
        link, is_secret = base.get_email_link(application)
        return render_to_response(
            'kgapplications/project_aed_introduction.html',
            {
                'actions': actions,
                'application': application, 'roles': roles,
                'link': link, 'is_secret': is_secret,
            },
            context_instance=RequestContext(request))


class StateStepShibboleth(Step):

    """ Invitation has been sent to applicant. """
    name = "Invitation sent"

    def view(self, request, application, label, roles, actions):
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

        elif application.content_type.model != 'applicant':
            status = "You are already registered in the system."
            form = None
            done = True

        elif (applicant.institute is not None and
                applicant.institute.saml_entityid is None):
            status = "Your institute does not have shibboleth registered."
            form = None
            done = True

        elif Institute.objects.filter(
                saml_entityid__isnull=False).count() == 0:
            status = "No institutes support shibboleth here."
            form = None
            done = True

        else:
            # shibboleth registration is required

            # Do construct the form
            form = saml.SAMLInstituteForm(
                request.POST or None,
                initial={'institute': applicant.institute})
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
                    url = base.get_url(request, application, roles, label)
                    if institute.saml_entityid is not None:
                        url = saml.build_shib_url(
                            request, url, institute.saml_entityid)
                    return HttpResponseRedirect(url)

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
            if 'cancel' in request.POST:
                return "cancel"
            if 'prev' in request.POST:
                return 'prev'

            if not done:
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

                    done = True
                else:
                    status = "Please login to SAML before proceeding."

        if request.method == 'POST' and done:
            for action in actions:
                if action in request.POST:
                    return action
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        # render the page
        return render_to_response(
            'kgapplications/project_aed_shibboleth.html',
            {'form': form, 'done': done, 'status': status,
                'actions': actions, 'roles': roles, 'application': application,
                'attrs': attrs, 'saml_session': saml_session, },
            context_instance=RequestContext(request))


class StateStepApplicant(Step):

    """ Application is open and user is can edit it."""
    name = "Open"

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        # Get the appropriate form
        status = None
        form = None

        if application.content_type.model != 'applicant':
            status = "You are already registered in the system."
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
            'kgapplications/project_aed_applicant.html',
            {
                'form': form,
                'application': application,
                'status': status, 'actions': actions, 'roles': roles,
            },
            context_instance=RequestContext(request))


class StateStepProject(base.State):

    """ Applicant is able to choose the project for the application. """
    name = "Choose project"

    def handle_ajax(self, request, application):
        resp = {}
        if 'leader' in request.POST:
            leader = Person.objects.get(pk=request.POST['leader'])
            project_list = leader.leads.filter(is_active=True)
            resp['project_list'] = \
                [(p.pk, six.text_type(p)) for p in project_list]

        elif 'terms' in request.POST:
            terms = request.POST['terms'].lower()
            try:
                project = Project.active.get(pid__icontains=terms)
                resp['project_list'] = [(project.pk, six.text_type(project))]
            except Project.DoesNotExist:
                resp['project_list'] = []
            except Project.MultipleObjectsReturned:
                resp['project_list'] = []
            leader_list = Person.active.filter(
                institute=application.applicant.institute,
                leads__is_active=True).distinct()
            if len(terms) >= 3:
                query = Q()
                for term in terms.split(' '):
                    q = Q(username__icontains=term)
                    q = q | Q(short_name__icontains=term)
                    q = q | Q(full_name__icontains=term)
                    query = query & q
                leader_list = leader_list.filter(query)
                resp['leader_list'] = [
                    (p.pk, "%s (%s)" % (p, p.username)) for p in leader_list]
            else:
                resp['error'] = "Please enter at lease three " \
                    "characters for search."
                resp['leader_list'] = []

        return resp

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if 'ajax' in request.POST:
            resp = self.handle_ajax(request, application)
            return HttpResponse(
                json.dumps(resp), content_type="application/json")

        form_models = {
            'common': forms.CommonApplicationForm,
            'new': forms.NewProjectApplicationForm,
            'existing': forms.ExistingProjectApplicationForm,
        }

        project_forms = {}

        for key, form in six.iteritems(form_models):
            project_forms[key] = form(
                request.POST or None, instance=application)

        if application.project is not None:
            project_forms["common"].initial = {'application_type': 'U'}
        elif application.name != "":
            project_forms["common"].initial = {'application_type': 'P'}

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
            'kgapplications/project_aed_project.html',
            {'forms': project_forms, 'project': project,
                'actions': actions, 'roles': roles,
                'application': application, },
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

    def view(self, request, application, label, roles, actions):
        """ Process the view request at the current step. """

        # if user is logged and and not applicant, steal the
        # application
        if 'is_applicant' in roles:
            # if we got this far, then we either we are logged in as applicant,
            # or we know the secret for this application.

            new_person = None
            reason = None
            details = None

            attrs, _ = saml.parse_attributes(request)
            saml_id = attrs['persistent_id']
            if saml_id is not None:
                query = Person.objects.filter(saml_id=saml_id)
                if application.content_type.model == "person":
                    query = query.exclude(pk=application.applicant.pk)
                if query.count() > 0:
                    new_person = Person.objects.get(saml_id=saml_id)
                    reason = "SAML id is already in use by existing person."
                    details = (
                        "It is not possible to continue this application " +
                        "as is because the saml identity already exists " +
                        "as a registered user.")
                del query

            if request.user.is_authenticated():
                new_person = request.user
                reason = "%s was logged in " \
                    "and accessed the secret URL." % new_person
                details = (
                    "If you want to access this application " +
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
                        log.change(
                            application.application_ptr,
                            "Stolen application from %s" % old_applicant)
                        messages.success(
                            request,
                            "Stolen application from %s" % old_applicant)
                        url = base.get_url(request, application, roles, label)
                        return HttpResponseRedirect(url)
                    else:
                        return render_to_response(
                            'kgapplications/project_aed_steal.html',
                            {'application': application, 'person': new_person,
                                'reason': reason, 'details': details, },
                            context_instance=RequestContext(request))

        # if the user is the leader, show him the leader specific page.
        if ('is_leader' in roles or 'is_delegate' in roles) \
                and 'is_admin' not in roles \
                and 'is_applicant' not in roles:
            actions = ['reopen']
            if 'reopen' in request.POST:
                return 'reopen'
            return render_to_response(
                'kgapplications/project_aed_for_leader.html',
                {'application': application,
                    'actions': actions, 'roles': roles, },
                context_instance=RequestContext(request))

        # otherwise do the default behaviour for StateWithSteps
        return super(StateApplicantEnteringDetails, self) \
            .view(request, application, label, roles, actions)


class StateWaitingForLeader(states.StateWaitingForApproval):

    """ We need the leader to provide approval. """
    name = "Waiting for leader"
    authorised_text = "a project leader"
    authorised_role = "project leader"

    def get_authorised_persons(self, application):
        return application.project.leaders.filter(
            is_active=True, login_enabled=True)

    def get_approve_form(self, request, application, roles):
        return forms.approve_project_form_generator(application, roles)


class StateWaitingForDelegate(states.StateWaitingForApproval):

    """ We need the delegate to provide approval. """
    name = "Waiting for delegate"
    authorised_text = "an institute delegate"
    authorised_role = "institute delegate"

    def get_authorised_persons(self, application):
        return application.institute.delegates \
            .filter(
                institutedelegate__send_email=True,
                is_active=True, login_enabled=True)

    def get_approve_form(self, request, application, roles):
        return forms.approve_project_form_generator(application, roles)


class StateWaitingForAdmin(states.StateWaitingForApproval):

    """ We need the administrator to provide approval. """
    name = "Waiting for administrator"
    authorised_text = "an administrator"
    authorised_role = "administrator"

    def get_authorised_persons(self, application):
        return Person.objects.filter(
            is_admin=True, is_active=True, login_enabled=True)

    def check_authorised(self, request, application, roles):
        """ Check the person's authorization. """
        return 'is_admin' in roles

    def get_approve_form(self, request, application, roles):
        return forms.admin_approve_project_form_generator(
            application, roles)

    def get_request_email_link(self, application):
        link, is_secret = base.get_admin_email_link(application)
        return link, is_secret


class StateDuplicateApplicant(base.State):

    """ Somebody has declared application is existing user. """
    name = "Duplicate Applicant"

    def enter_state(self, request, application):
        authorised_persons = Person.objects.filter(
            is_admin=True, is_active=True, login_enabled=True)
        link, is_secret = base.get_registration_email_link(application)
        emails.send_duplicate_email(
            "an administrator",
            "administrator",
            authorised_persons,
            application,
            link, is_secret)

    def view(self, request, application, label, roles, actions):
        # if not admin, don't allow reopen
        if 'is_admin' not in roles:
            if 'reopen' in actions:
                actions.remove('reopen')
        if label is None and 'is_admin' in roles:
            form = forms.ApplicantReplace(
                data=request.POST or None,
                application=application)

            if request.method == 'POST':
                if 'replace' in request.POST:
                    if form.is_valid():
                        form.save()
                        return "reopen"
                else:
                    for action in actions:
                        if action in request.POST:
                            return action
                    return HttpResponseBadRequest("<h1>Bad Request</h1>")

            return render_to_response(
                'kgapplications/project_duplicate_applicant.html',
                {'application': application, 'form': form,
                    'actions': actions, 'roles': roles, },
                context_instance=RequestContext(request))
        return super(StateDuplicateApplicant, self).view(
            request, application, label, roles, actions)


class StateArchived(states.StateCompleted):

    """ This application is archived. """
    name = "Archived"


class TransitionSplit(base.Transition):

    """ A transition after application submitted. """

    def __init__(self, on_existing_project, on_new_project, on_error):
        super(TransitionSplit, self).__init__()
        self._on_existing_project = on_existing_project
        self._on_new_project = on_new_project
        self._on_error = on_error

    def get_next_state(self, request, application, roles):
        """ Retrieve the next state. """
        # Do we need to wait for leader or delegate approval?
        if application.project is None:
            return self._on_new_project
        else:
            return self._on_existing_project


def get_application_state_machine():
    """ Get the default state machine for applications. """
    open_transition = states.TransitionOpen(on_success='O')
    split = TransitionSplit(
        on_existing_project='L', on_new_project='D', on_error="R")

    state_machine = base.StateMachine()
    state_machine.add_state(
        StateApplicantEnteringDetails(), 'O',
        {'cancel': 'R', 'reopen': open_transition, 'duplicate': 'DUP',
            'submit': states.TransitionSubmit(
                on_success=split, on_error="R")})
    state_machine.add_state(
        StateWaitingForLeader(), 'L',
        {'cancel': 'R', 'approve': 'K', 'duplicate': 'DUP', })
    state_machine.add_state(
        StateWaitingForDelegate(), 'D',
        {'cancel': 'R', 'approve': 'K', 'duplicate': 'DUP', })
    state_machine.add_state(
        StateWaitingForAdmin(), 'K',
        {'cancel': 'R', 'duplicate': 'DUP',
            'approve': states.TransitionApprove(
                on_password_needed='P', on_password_ok='C', on_error="R")})
    state_machine.add_state(
        states.StatePassword(), 'P',
        {'submit': 'C', })
    state_machine.add_state(
        states.StateCompleted(), 'C',
        {'archive': 'A', })
    state_machine.add_state(
        StateArchived(), 'A',
        {})
    state_machine.add_state(
        states.StateDeclined(), 'R',
        {'reopen': open_transition, })
    state_machine.add_state(
        StateDuplicateApplicant(), 'DUP',
        {'reopen': open_transition, 'cancel': 'R', })
    state_machine.set_first_state(open_transition)
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


def register():
    base.setup_application_type(
        ProjectApplication, get_application_state_machine())


def get_applicant_from_email(email):
    try:
        applicant = Person.active.get(email=email)
        existing_person = True
    except Person.DoesNotExist:
        applicant, _ = Applicant.objects.get_or_create(email=email)
        existing_person = False
    return applicant, existing_person


def _send_invitation(request, project):
    """ The logged in project leader OR administrator wants to invite somebody.
    """
    form = forms.InviteUserApplicationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():

            email = form.cleaned_data['email']
            applicant, existing_person = get_applicant_from_email(email)

            if existing_person and 'existing' not in request.POST:
                return render_to_response(
                    'kgapplications/project_common_invite_existing.html',
                    {'form': form, 'person': applicant},
                    context_instance=RequestContext(request))

            application = form.save(commit=False)
            application.applicant = applicant
            application.project = project
            application.save()
            state_machine = get_application_state_machine()
            response = state_machine.start(request, application)
            return response

    return render_to_response(
        'kgapplications/project_common_invite_other.html',
        {'form': form, 'project': project, },
        context_instance=RequestContext(request))


@login_required
def send_invitation(request, project_id=None):
    """ The logged in project leader wants to invite somebody to their project.
    """

    project = None
    if project_id is not None:
        project = get_object_or_404(Project, id=project_id)

    if project is None:

        if not is_admin(request):
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    else:

        if not project.can_edit(request):
            return HttpResponseForbidden('<h1>Access Denied</h1>')

    return _send_invitation(request, project)


def new_application(request):
    """ A new application by a user to start a new project. """
    # Note default kgapplications/index.html will display error if user logged
    # in.
    if not settings.ALLOW_REGISTRATIONS:
        return render_to_response(
            'kgapplications/project_common_disabled.html',
            {},
            context_instance=RequestContext(request))

    roles = {'is_applicant', 'is_authorised'}

    if not request.user.is_authenticated():
        attrs, _ = saml.parse_attributes(request)
        defaults = {'email': attrs['email']}
        form = forms.UnauthenticatedInviteUserApplicationForm(
            request.POST or None, initial=defaults)
        if request.method == 'POST':
            if form.is_valid():
                email = form.cleaned_data['email']
                applicant, existing_person = get_applicant_from_email(email)
                assert not existing_person

                application = ProjectApplication()
                application.applicant = applicant
                application.save()

                state_machine = get_application_state_machine()
                state_machine.start(request, application, roles)
                # we do not show unauthenticated users the application at this
                # stage.
                url = reverse('index')
                return HttpResponseRedirect(url)
        return render_to_response(
            'kgapplications/project_common_invite_unauthenticated.html',
            {'form': form, },
            context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            person = request.user

            application = ProjectApplication()
            application.applicant = person
            application.save()

            state_machine = get_application_state_machine()
            response = state_machine.start(request, application, roles)
            return response
        return render_to_response(
            'kgapplications/project_common_invite_authenticated.html',
            {},
            context_instance=RequestContext(request))
