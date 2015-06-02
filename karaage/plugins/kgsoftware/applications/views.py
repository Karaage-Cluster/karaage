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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseBadRequest

from karaage.common.decorators import login_required
from karaage.people.models import Person

from karaage.plugins.kgapplications.views import base, states

from .forms import ApproveSoftwareForm
from .models import SoftwareApplication


class StateIntroduction(base.State):
    """ Invitation has been sent to applicant. """
    name = "Read introduction"

    def view(self, request, application, label, roles, actions):
        """ Django view method. """
        if label is None and \
                'is_applicant' in roles and 'is_admin' not in roles:
            for action in actions:
                if action in request.POST:
                    return action
            link, is_secret = base.get_email_link(application)
            return render_to_response(
                'kgapplications/software_introduction.html',
                {'actions': actions, 'application': application,
                    'roles': roles, 'link': link, 'is_secret': is_secret},
                context_instance=RequestContext(request))
        return super(StateIntroduction, self).view(
            request, application, label, roles, actions)


class StateWaitingForAdmin(states.StateWaitingForApproval):
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


def get_application_state_machine():
    """ Get the default state machine for applications. """
    open_transition = states.TransitionOpen(on_success='O')

    state_machine = base.StateMachine()
    state_machine.add_state(
        StateIntroduction(), 'O',
        {'cancel': 'R',
            'submit': states.TransitionSubmit(on_success='K', on_error="R")})
    state_machine.add_state(
        StateWaitingForAdmin(), 'K',
        {'cancel': 'R',
            'approve': states.TransitionApprove(
                on_password_needed='R', on_password_ok='C', on_error="R")})
    state_machine.add_state(
        states.StateCompleted(), 'C',
        {})
    state_machine.add_state(
        states.StateDeclined(), 'R',
        {'reopen': open_transition, })
    state_machine.set_first_state(open_transition)
    return state_machine


def register():
    base.setup_application_type(
        SoftwareApplication, get_application_state_machine())


@login_required
def new_application(request, software_license):
    # Called automatically by hook.
    assert software_license is not None

    if request.method != 'POST':
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    application = SoftwareApplication()
    application.applicant = request.user
    application.software_license = software_license
    application.save()

    state_machine = get_application_state_machine()
    response = state_machine.start(request, application, {})
    return response
