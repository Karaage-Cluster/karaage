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
from django.http import HttpResponseBadRequest

from karaage.common.decorators import login_required
from karaage.software.models import SoftwareLicense
from karaage.people.models import Person
from karaage.applications.models import SoftwareApplication
import karaage.applications.emails as emails
import karaage.applications.forms as forms
import karaage.applications.views.base as base
import karaage.applications.views.user as user
import karaage.applications.views.common as common


class StateIntroduction(base.State):
    """ Invitation has been sent to applicant. """
    name = "Read introduction"

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


class StateWaitingForAdmin(common.StateWaitingForApproval):
    """ We need the administrator to provide approval. """
    name = "Waiting for administrator"
    authorised_text = "an administrator"

    def get_authorised_persons(self, application):
        return Person.objects.filter(is_admin=True)

    def check_authorised(self, request, application, auth):
        """ Check the person's authorization. """
        return auth['is_admin']

    def get_approve_form(self, request, application, auth):
        return forms.ApproveSoftwareForm


def get_application_state_machine():
    """ Get the default state machine for applications. """
    Open = common.TransitionOpen(on_success='O')

    state_machine = base.StateMachine()
    state_machine.add_state(StateIntroduction(), 'O',
            { 'cancel': 'R',
                'submit':  common.TransitionSubmit(on_success='K', on_error="R")})
    state_machine.add_state(StateWaitingForAdmin(), 'K',
            { 'cancel': 'R',
                'approve': common.TransitionApprove(on_password_needed='R', on_password_ok='C', on_error="R")})
    state_machine.add_state(common.StateCompleted(), 'C',
            {})
    state_machine.add_state(common.StateDeclined(), 'R',
            { 'reopen': Open,  })
    state_machine.set_first_state(Open)
    return state_machine


def register():
    base.setup_application_type(SoftwareApplication, get_application_state_machine())


@login_required
def new_application(request, software_license_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    try:
        license = SoftwareLicense.objects.get(pk=software_license_id)
    except SoftwareLicense.DoesNotExist:
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    application = SoftwareApplication()
    application.applicant = request.user
    application.software_license = license
    application.save()

    state_machine = get_application_state_machine()
    response = state_machine.start(request, application, {})
    return response
