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

""" This file shows the project application views using a state machine. """

from django.conf import settings
from django.http import HttpResponseBadRequest

from karaage.common.decorators import login_required
from karaage.plugins.kgapplications.views import base

from .models import SoftwareApplication


def get_application_state_machine():
    """Get the default state machine for applications."""
    config = settings.APPLICATION_SOFTWARE
    state_machine = base.StateMachine(config)
    return state_machine


def register():
    base.setup_application_type(SoftwareApplication, get_application_state_machine())


@login_required
def new_application(request, software_license):
    # Called automatically by hook.
    assert software_license is not None

    if request.method != "POST":
        return HttpResponseBadRequest("<h1>Bad Request</h1>")

    application = SoftwareApplication()
    application.new_applicant = None
    application.existing_person = request.user
    application.software_license = software_license
    application.save()

    state_machine = get_application_state_machine()
    response = state_machine.start(request, application, {})
    return response
