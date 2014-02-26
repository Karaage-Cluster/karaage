# Copyright 2007-2014 VPAC
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

from django.conf.urls import patterns, url, include

import karaage.applications.models as models
import karaage.applications.views.software as software

urlpatterns = patterns('',
    url(r'^applications/', include('karaage.applications.urls')),
)

def context(request):
    ctx = {}
    if request.user.is_authenticated():
        person = request.user
        my_applications = models.Application.objects.get_for_applicant(person)
        requires_attention = models.Application.objects.requires_attention(request)

        ctx['pending_applications'] = (
                  my_applications.count() + requires_attention.count()
        )
    return ctx

def approve_join_software(request, software_license):
    return software.new_application(request, software_license)

def is_approve_join_software_pending(request, software_license):
    person = request.user
    query = models.SoftwareApplication.objects.get_for_applicant(person)
    query = query.filter(software_license=software_license)
    return query.count() > 0
