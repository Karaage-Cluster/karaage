# Copyright 2007-2013 VPAC
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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseBadRequest

from karaage.emails.forms import EmailForm
from karaage.common.decorators import login_required
from karaage.software.models import SoftwareLicense
from karaage.applications.models import SoftwareRequest
import karaage.applications.emails as emails
import karaage.applications.views.base as base
import karaage.applications.views.user as user


class State(base.State):
    """ A abstract class that is the base for all application states. """
    name = "Abstract State"

    def view(self, request, application, label, auth, actions):
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
        actions = tmp_actions

        # process the request in default view
        if request.method == "GET":
            return render_to_response(
                    'applications/software_common_detail.html',
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


class StateIntroduction(State):
    """ Invitation has been sent to applicant. """
    name = "Read introduction"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        application.reopen()
        link, is_secret = base.get_email_link(application)
        emails.send_software_invite_email(application, link, is_secret)
        messages.success(
                request,
                "Sent an invitation to %s." %
                (application.applicant.email))


    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label is None and auth['is_applicant'] and not auth['is_admin']:
            for action in actions:
                if action in request.POST:
                    return action
            link, is_secret = base.get_email_link(application)
            return render_to_response('applications/software_introduction.html',
                    {'actions': actions, 'application': application, 'auth': auth,
                    'link': link, 'is_secret': is_secret },
                    context_instance=RequestContext(request))
        return super(StateIntroduction, self).view(request, application, label, auth, actions)


class StateWaitingForAdmin(State):
    """ We need the administrator to provide approval. """
    name = "Waiting for administrator"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        emails.send_admin_software_request_email(application)

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label == "approve" and auth['is_admin']:
            tmp_actions = []
            if 'approve' in actions:
                tmp_actions.append("approve")
            if 'duplicate' in actions:
                tmp_actions.append("approve")
            actions = tmp_actions
            if request.method == 'POST':
                return "approve"
            return render_to_response(
                    'applications/software_admin_approve_for_admin.html',
                    {'application': application,
                        'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        elif label == "decline" and auth['is_admin']:
            actions = [ 'cancel' ]
            if request.method == 'POST':
                form = EmailForm(request.POST)
                if form.is_valid():
                    to_email = application.applicant.email
                    subject, body = form.get_data()
                    emails.send_mail(
                            subject, body,
                            settings.ACCOUNTS_EMAIL, [to_email])
                    return "cancel"
            else:
                link, is_secret = base.get_email_link(application)
                subject, body = emails.render_email(
                        'software_declined',
                        {'receiver': application.applicant,
                        'application': application,
                        'link': link, 'is_secret': is_secret})
                initial_data = {'body': body, 'subject': subject}
                form = EmailForm(initial=initial_data)
            return render_to_response(
                    'applications/software_admin_decline_for_admin.html',
                    {'application': application, 'form': form,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateWaitingForAdmin, self).view(
                request, application, label, auth, actions)


class StateCompleted(State):
    """ This application is completed and processed. """
    name = "Completed"


class StateDeclined(State):
    """ This application declined. """
    name = "Declined"

    def enter_state(self, request, application):
        """ This is becoming the new current state. """
        application.decline()

    def view(self, request, application, label, auth, actions):
        """ Django view method. """
        if label is None and auth['is_applicant'] and not auth['is_admin']:
            # applicant, admin, leader can reopen an application
            if 'reopen' in request.POST:
                return 'reopen'
            return render_to_response(
                    'applications/software_declined_for_applicant.html',
                    {'application': application,
                    'actions': actions, 'auth': auth},
                    context_instance=RequestContext(request))
        return super(StateDeclined, self).view(
                request, application, label, auth, actions)


class TransitionSubmit(base.Transition):
    """ A transition after application submitted. """
    def __init__(self, on_success, on_error):
        self._on_success = on_success
        self._on_error = on_error

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """

        # Check for serious errors in submission.
        # Should only happen in rare circumstances.
        errors = application.check()
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return self._on_error

        # mark as submitted
        application.submit()

        return self._on_success


class TransitionApprove(base.Transition):
    """ A transition after application fully approved. """
    def __init__(self, on_success, on_error):
        self._on_success = on_success
        self._on_error = on_error

    def get_next_state(self, request, application, auth):
        """ Retrieve the next state. """
        # Check for serious errors in submission.
        # Should only happen in rare circumstances.
        errors = application.check()
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return self._on_error

        # approve application
        approved_by = request.user
        created_person = application.approve(approved_by)
        assert created_person == False

        # send email
        emails.send_software_approved_email(application)

        # continue
        return self._on_success


def get_application_state_machine():
    """ Get the default state machine for applications. """
    state_machine = base.StateMachine()
    state_machine.add_state(StateIntroduction(), 'O',
            { 'cancel': 'R',
                'submit':  TransitionSubmit(on_success='K', on_error="R")})
    state_machine.add_state(StateWaitingForAdmin(), 'K',
            { 'cancel': 'R',
                'approve': TransitionApprove(on_success='C', on_error="R")})
    state_machine.add_state(StateCompleted(), 'C',
            {})
    state_machine.add_state(StateDeclined(), 'R',
            { 'reopen': 'O',  })
    return state_machine

def register():
    user.setup_application_type(SoftwareRequest, get_application_state_machine())

@login_required
def new_application(request, software_license_id):
    try:
        license = SoftwareLicense.objects.get(pk=software_license_id)
    except SoftwareLicense.DoesNotExist:
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    application = SoftwareRequest()
    application.applicant = request.user
    application.software_license = license
    application.save()

    state_machine = get_application_state_machine()
    response = state_machine.start(request, application, {})
    return response
