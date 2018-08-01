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

""" This file is for common state or transitions that can be shared. """

from django.conf import settings
from django.contrib import messages
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render

from karaage.emails.forms import EmailForm
from karaage.people.models import Person
from karaage.plugins.kgsoftware.applications.forms import ApproveSoftwareForm

from . import base
from .. import emails, forms


class StateWaitingForApproval(base.State):
    """ We need the somebody to provide approval. """
    name = "Waiting for X"
    authorised_text = "X"
    authorised_role = None
    template_approve = "kgapplications/common_approve.html"
    template_decline = "kgapplications/common_decline.html"
    actions = {'approve', 'duplicate', 'cancel'}

    def get_authorised_persons(self, application):
        raise NotImplementedError()

    def get_email_persons(self, application):
        # by default, email all authorised persons
        return self.get_authorised_persons(application)

    def get_approve_form(self, request, application, roles):
        raise NotImplementedError()

    def check_can_approve(self, request, application, roles):
        """ Check the person's authorization. """
        try:
            authorised_persons = self.get_authorised_persons(application)
            authorised_persons.get(pk=request.user.pk)
            return True
        except Person.DoesNotExist:
            return False

    def get_actions(self, request, application, roles):
        actions = set(self.actions)
        if not self.check_can_approve(request, application, roles):
            actions.remove('approve')
            actions.remove('duplicate')
        return actions

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        authorised_persons = self.get_email_persons(application)
        link, is_secret = self.get_request_email_link(application)
        emails.send_request_email(
            self.authorised_text,
            self.authorised_role,
            authorised_persons,
            application,
            link, is_secret)

    def get_request_email_link(self, application):
        link, is_secret = base.get_registration_email_link(application)
        return link, is_secret

    def get_next_action(self, request, application, label, roles):
        """ Django view method. """
        actions = self.get_actions(request, application, roles)
        if label == "approve" and 'approve' in actions:
            application_form = self.get_approve_form(
                request, application, roles)
            form = application_form(request.POST or None, instance=application)
            if request.method == 'POST':
                if 'back' in request.POST:
                    url = base.get_url(request, application, roles)
                    return HttpResponseRedirect(url)
                if 'approve' in request.POST and form.is_valid():
                    form.save()
                    return "approve"
            return render(
                template_name=self.template_approve,
                context={
                    'application': application,
                    'form': form,
                    'authorised_text': self.authorised_text,
                    'actions': self.get_actions(request, application, roles),
                    'roles': roles
                },
                request=request)
        elif label == "cancel" and 'cancel' in actions:
            if request.method == 'POST':
                form = EmailForm(request.POST)
                if 'back' in request.POST:
                    url = base.get_url(request, application, roles)
                    return HttpResponseRedirect(url)
                if 'cancel' in request.POST and form.is_valid():
                    to_email = application.applicant.email
                    subject, body = form.get_data()
                    emails.send_mail(
                        subject, body,
                        settings.ACCOUNTS_EMAIL, [to_email])
                    return "cancel"
            else:
                link, is_secret = base.get_email_link(application)
                subject, body = emails.render_email(
                    'common_declined',
                    {'receiver': application.applicant,
                        'authorised_text': self.authorised_text,
                        'application': application,
                        'link': link, 'is_secret': is_secret})
                initial_data = {'body': body, 'subject': subject}
                form = EmailForm(initial=initial_data)
            return render(
                template_name=self.template_decline,
                context={
                    'application': application,
                    'form': form,
                    'authorised_text': self.authorised_text,
                    'actions': self.get_actions(request, application, roles),
                    'roles': roles
                },
                request=request)
        elif request.method == "POST":
            for action in ['approve', 'cancel']:
                if action in request.POST:
                    url = base.get_url(request, application, roles, action)
                    return HttpResponseRedirect(url)

        # Not parent class method will do the same thing, however this makes it
        # explicit.
        if label is not None:
            return HttpResponseBadRequest("<h1>Bad Request</h1>")

        self.context = {
            'authorised_text': self.authorised_text,
        }
        return super(StateWaitingForApproval, self).get_next_action(
            request, application, label, roles)


class StatePassword(base.State):
    """ This application is completed and processed. """
    name = "Password"
    actions = {'cancel', 'submit'}

    def get_next_action(self, request, application, label, roles):
        """ Django view method. """
        actions = self.get_actions(request, application, roles)
        if label is None and 'is_applicant' in roles:
            assert application.content_type.model == 'person'
            if application.applicant.has_usable_password():
                form = forms.PersonVerifyPassword(
                    data=request.POST or None, person=application.applicant)
                form_type = "verify"
            else:
                form = forms.PersonSetPassword(
                    data=request.POST or None, person=application.applicant)
                form_type = "set"
            if request.method == 'POST':
                if 'cancel' in request.POST:
                    return 'cancel'
                if form.is_valid():
                    form.save()
                    messages.success(
                        request, 'Password updated. New accounts activated.')
                    for action in actions:
                        if action in request.POST:
                            return action
                    return HttpResponseBadRequest("<h1>Bad Request</h1>")
            return render(
                template_name='kgapplications/common_password.html',
                context={
                    'application': application,
                    'form': form,
                    'actions': actions,
                    'roles': roles,
                    'type': form_type
                },
                request=request)
        return super(StatePassword, self).get_next_action(request, application, label, roles)


class StateCompleted(base.State):
    """ This application is completed and processed. """
    name = "Completed"
    actions = {'archive'}

    def get_actions(self, request, application, roles):
        actions = set(self.actions)
        if 'is_admin' not in roles:
            actions.remove('archive')
        return actions


class StateDeclined(base.State):
    """ This application declined. """
    name = "Declined"
    actions = {'reopen', 'archive'}

    def get_actions(self, request, application, roles):
        actions = set(self.actions)
        if 'is_admin' not in roles:
            actions.remove('archive')
        return actions

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        application.decline()

    def get_next_action(self, request, application, label, roles):
        """ Django view method. """
        actions = self.get_actions(request, application, roles)
        if label is None and \
                'is_applicant' in roles and 'is_admin' not in roles:
            # applicant, admin, leader can reopen an application
            for action in actions:
                if action in request.POST:
                    return action
            return render(
                template_name='kgapplications/common_declined.html',
                context={
                    'application': application,
                    'actions': actions,
                    'roles': roles
                },
                request=request)
        return super(StateDeclined, self).get_next_action(
            request, application, label, roles)


class StateWaitingForDelegate(StateWaitingForApproval):

    """ We need the delegate to provide approval. """
    name = "Waiting for delegate"
    authorised_text = "an institute delegate"
    authorised_role = "institute delegate"

    def get_authorised_persons(self, application):
        return application.institute.delegates \
            .filter(is_active=True, login_enabled=True)

    def get_email_persons(self, application):
        return application.institute.delegates \
            .filter(
                institutedelegate__send_email=True,
                is_active=True, login_enabled=True)

    def get_approve_form(self, request, application, roles):
        return forms.approve_project_form_generator(application, roles)


class StateWaitingForAdmin(StateWaitingForApproval):

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
    actions = {'cancel', 'reopen'}

    def get_actions(self, request, reapplication, roles):
        actions = set(self.actions)
        if 'is_admin' not in roles:
            actions.remove('reopen')
        return actions

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

    def get_next_action(self, request, application, label, roles):
        # if not admin, don't allow reopen
        actions = self.get_actions(request, application, roles)
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

            return render(
                template_name='kgapplications/'
                              'project_duplicate_applicant.html',
                context={'application': application, 'form': form,
                         'actions': actions, 'roles': roles, },
                request=request)
        return super(StateDuplicateApplicant, self).get_next_action(
            request, application, label, roles)


class StateArchived(StateCompleted):

    """ This application is archived. """
    name = "Archived"
    actions = {'reopen'}

    def get_actions(self, request, application, roles):
        actions = set(self.actions)
        if 'is_admin' not in roles:
            actions.remove('reopen')
        return actions


class Step(object):

    """ A single step in a StateWithStep state. """

    def view(self, request, application, label, roles, actions):
        raise NotImplementedError()


class StateWithSteps(base.State):

    """ A state that has a number of steps to complete. """

    def __init__(self, config):
        self._first_step = None
        self._steps = {}
        self._order = []
        super(StateWithSteps, self).__init__(config)

    def add_step(self, step, step_id):
        """ Add a step to the list. The first step added becomes the initial
        step. """
        assert step_id not in self._steps
        assert step_id not in self._order
        assert isinstance(step, Step)

        self._steps[step_id] = step
        self._order.append(step_id)

    def get_next_action(self, request, application, label, roles):
        """ Process the get_next_action request at the current step. """
        actions = self.get_actions(request, application, roles)

        # if the user is not the applicant, the steps don't apply.
        if 'is_applicant' not in roles:
            return super(StateWithSteps, self).get_next_action(
                request, application, label, roles)

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

        # Something went wrong.
        return HttpResponseBadRequest("<h1>Bad Request</h1>")


class StateWaitingForLeader(StateWaitingForApproval):

    """ We need the leader to provide approval. """
    name = "Waiting for leader"
    authorised_text = "a project leader"
    authorised_role = "project leader"

    def get_authorised_persons(self, application):
        return application.project.leaders.filter(
            is_active=True, login_enabled=True)

    def get_approve_form(self, request, application, roles):
        return forms.approve_project_form_generator(application, roles)


class StateIntroduction(base.State):
    """ Invitation has been sent to applicant. """
    name = "Read introduction"
    actions = {'cancel', 'submit'}

    def get_next_action(self, request, application, label, roles):
        """ Django get_next_action method. """
        actions = self.get_actions(request, application, roles)
        if label is None and \
                'is_applicant' in roles and 'is_admin' not in roles:
            for action in actions:
                if action in request.POST:
                    return action
            link, is_secret = base.get_email_link(application)
            return render(
                template_name='kgapplications/software_introduction.html',
                context={
                    'actions': actions,
                    'application': application,
                    'roles': roles,
                    'link': link,
                    'is_secret': is_secret
                },
                request=request)
        return super(StateIntroduction, self).get_next_action(
            request, application, label, roles)


class StateWaitingForAdminSoftware(StateWaitingForApproval):
    """ We need the administrator to provide approval. """
    name = "Waiting for administrator"
    authorised_text = "an administrator"
    authorised_role = "administrator"

    def get_authorised_persons(self, application):
        return Person.objects.filter(is_admin=True)

    def check_can_approve(self, request, application, roles):
        """ Check the person's authorization. """
        return 'is_admin' in roles

    def get_approve_form(self, request, application, roles):
        return ApproveSoftwareForm
