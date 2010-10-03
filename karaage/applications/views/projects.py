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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

import datetime

from karaage.applications.models import UserApplication, Applicant, ProjectApplication, Application
from karaage.applications.forms import ProjectApplicationForm, UserApplicantForm, LeaderApproveUserApplicationForm, LeaderInviteUserApplicationForm
from karaage.applications.emails import send_account_request_email, send_account_approved_email, send_user_invite_email
from karaage.people.models import Person
from karaage.projects.models import Project


def do_projectapplication(request, token=None, application_form=ProjectApplicationForm):
    if request.user.is_authenticated():
        messages.info(request, "You are already logged in")
        return HttpResponseRedirect(reverse('kg_user_profile'))

    if token:
        application = get_object_or_404(ProjectApplication, secret_token=token)
        if application.state not in (Application.NEW, Application.OPEN):
            raise Http404
        applicant = application.applicant
        application.state = Application.OPEN
        application.save()
    else:
        if not settings.ALLOW_REGISTRATIONS:
            return render_to_response('applications/registrations_disabled.html', {}, context_instance=RequestContext(request)) 
        application = None
        applicant = None
    if request.method == 'POST':
        form = application_form(request.POST, instance=application)
        applicant_form = UserApplicantForm(request.POST, instance=applicant)
        if form.is_valid() and applicant_form.is_valid():
            applicant = applicant_form.save()
            application = form.save(commit=False)
            application.applicant = applicant
            application.save()
            application.submitted_date = datetime.datetime.now()
            application.state = Application.WAITING_FOR_DELEGATE
            application.save()
            #send_project_request_email(application)
            return HttpResponseRedirect(reverse('kg_application_done',  args=[application.secret_token]))
    else:
        form = application_form(instance=application)
        applicant_form = UserApplicantForm(instance=applicant)
    
    return render_to_response('applications/projectapplication_form.html', {'form': form, 'applicant_form': applicant_form, 'application': application}, context_instance=RequestContext(request)) 


