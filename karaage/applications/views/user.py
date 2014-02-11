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


@login_required
def application_list(request):
    """ a logged in user wants to see all his pending applications. """
    person = request.user
    my_applications = application.objects.get_for_applicant(person)
    requires_attention = application.objects.requires_attention(person)

    return render_to_response(
            'applications/application_list.html',
            {
            'my_applications': my_applications,
            'requires_attention': requires_attention,
            },
            context_instance=requestcontext(request))


#@login_required
#def application_detail(request, application_id, state=None, label=None):
#    """ An authenticated user is trying to access an application. """
#    application = base.get_application(pk=application_id)
#    state_machine = base.get_state_machine(application)
#    return state_machine.process(request, application, state, label, {})

#
#def application_unauthenticated(request, token, state=None, label=None):
#    """ An unauthenticated user is trying to access an application. """
#    application = base.get_application(
#                secret_token=token, expires__gt=datetime.datetime.now())
#
#    # redirect user to real url if possible.
#    if request.user.is_authenticated():
#        if request.user == application.applicant:
#            url = base.get_url(request, application, {'is_applicant': True}, label)
#            return HttpResponseRedirect(url)
#
#    state_machine = base.get_state_machine(application)
#    return state_machine.process(request, application, state, label,
#            { 'is_applicant': True })
#
