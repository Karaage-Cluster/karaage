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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.defaultfilters import wordwrap

import datetime

from karaage.common.decorators import login_required
from karaage.software.models import Software, SoftwareLicenseAgreement


@login_required
def add_package_list(request):

    person = request.user

    software_list = []
    for s in Software.objects.filter(softwarelicense__isnull=False).distinct():
        data = {'software': s}
        license_agreements = SoftwareLicenseAgreement.objects.filter(user=person, license__package=s)
        if license_agreements.count() > 0:
            la = license_agreements.latest()
            data['accepted'] = True
            data['accepted_date'] = la.date
        software_list.append(data)

    return render_to_response('software/add_package_list.html', locals(), context_instance=RequestContext(request))


@login_required
def add_package(request, software_id):

    software = get_object_or_404(Software, pk=software_id)
    software_license = software.get_current_license()
    person = request.user

    if software_license is None:
        raise Http404("Package '%s' has no software license." % (software))

    if request.method == 'POST':

        if software.restricted:
            return HttpResponseRedirect(reverse('kg_application_software_new', args=[software_license.pk]))
        else:
            SoftwareLicenseAgreement.objects.create(
                user=person,
                license=software_license,
                date=datetime.datetime.today(),
                )
            person.add_group(software.group)

        return HttpResponseRedirect(reverse('kg_user_profile_software'))

    return render_to_response('software/accept_license.html', locals(), context_instance=RequestContext(request))


@login_required
def license_txt(request, software_id):

    software = get_object_or_404(Software, pk=software_id)
    software_license = software.get_current_license()

    return HttpResponse(wordwrap(software_license.text, 80), mimetype="text/plain")
