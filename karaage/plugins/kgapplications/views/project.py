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
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from karaage.common import is_admin, saml
from karaage.common.decorators import login_required
from karaage.people.models import Person
from karaage.projects.models import Project

from . import base
from .. import forms
from ..models import Applicant, ProjectApplication


def get_application_state_machine():
    """ Get the default state machine for applications. """
    config = settings.APPLICATION_PROJECT
    state_machine = base.StateMachine(config)
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
                return render(
                    template_name='kgapplications/'
                                  'project_common_invite_existing.html',
                    context={'form': form, 'person': applicant},
                    request=request)

            application = form.save(commit=False)
            application.applicant = applicant
            application.project = project
            application.save()
            state_machine = get_application_state_machine()
            response = state_machine.start(request, application)
            return response

    return render(
        template_name='kgapplications/project_common_invite_other.html',
        context={'form': form, 'project': project, },
        request=request)


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
        return render(
            template_name='kgapplications/project_common_disabled.html',
            context={},
            request=request)

    roles = {'is_applicant', 'is_authorised'}

    if not request.user.is_authenticated:
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
        return render(
            template_name='kgapplications/'
            'project_common_invite_unauthenticated.html',
            context={'form': form, },
            request=request)
    else:
        if request.method == 'POST':
            person = request.user

            application = ProjectApplication()
            application.applicant = person
            application.save()

            state_machine = get_application_state_machine()
            response = state_machine.start(request, application, roles)
            return response
        return render(
            template_name='kgapplications/'
            'project_common_invite_authenticated.html',
            context={},
            request=request)
