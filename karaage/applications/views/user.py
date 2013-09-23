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

""" This file shows the application views.  """

import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.db.models import Q

from karaage.common.decorators import login_required, admin_required
from karaage.applications.models import Application
import karaage.applications.views.base as base


def _get_application(**kwargs):
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

@login_required
def application_detail(request, application_id, state=None, label=None):
    """ An authenticated user is trying to access an application. """
    application = _get_application(pk=application_id)
    state_machine = get_state_machine(application)
    return state_machine.process(request, application, state, label, {})

@admin_required
def application_detail_admin(request, application_id, state=None, label=None):
    """ An authenticated admin is trying to access an application. """
    application = _get_application(pk=application_id)
    state_machine = get_state_machine(application)
    return state_machine.process(request, application, state, label, { 'is_admin': True })


def application_unauthenticated(request, token, state=None, label=None):
    """ An unauthenticated user is trying to access an application. """
    application = _get_application(
                secret_token=token, expires__gt=datetime.datetime.now())

    # redirect user to real url if possible.
    if request.user.is_authenticated():
        if request.user == application.applicant:
            url = base.get_url(request, application, {'is_applicant': True}, label)
            return HttpResponseRedirect(url)

    state_machine = get_state_machine(application)
    return state_machine.process(request, application, state, label,
            { 'is_applicant': True })

@login_required
def pending_applications(request):
    """ A logged in user wants to see all his pending applications. """
    person = request.user
    my_applications = Application.objects.get_for_applicant(person)
    requires_attention = Application.objects.requires_attention(person)

    return render_to_response(
            'applications/application_list.html',
            {
            'my_applications': my_applications,
            'requires_attention': requires_attention,
            },
            context_instance=RequestContext(request))

