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
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.contrib import messages

from karaage.applications.models import UserApplication, Applicant
from karaage.applications.forms import AdminUserApplicationForm as UserApplicationForm, ApplicantForm


@permission_required('applications.add_userapplication')
def add_edit_userapplication(request, application_id=None):
    
    if application_id:
        application = get_object_or_404(UserApplication, pk=application_id)
        applicant = application.applicant
    else:
        application = None
        applicant = None

    if request.method == 'POST':
        form = UserApplicationForm(request.POST, instance=application)
        applicant_form = ApplicantForm(request.POST, instance=applicant)

        if form.is_valid() and applicant_form.is_valid():
            applicant = applicant_form.save()
            application = form.save(commit=False)
            application.applicant
            application.save()
            application = form.save()
            return HttpResponseRedirect(application.get_absolute_url())
        
    else:
        form = UserApplicationForm(instance=application)
        applicant_form = ApplicantForm(instance=applicant)

    return render_to_response('applications/admin_userapplication_form.html', {'form': form, 'applicant_form': applicant_form, 'application': application}, context_instance=RequestContext(request)) 
