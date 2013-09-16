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
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect

from karaage.common.filterspecs import Filter, FilterBar

from karaage.common.decorators import admin_required
from karaage.applications.models import Applicant, Application
from karaage.applications.forms import ApplicantForm
from karaage.common import log
import karaage.common as util


@admin_required
def application_list(request):

    apps = Application.objects.select_related().order_by('-id')

    try:
        page_no = int(request.GET.get('page', 1))
    except ValueError:
        page_no = 1

    if 'state' in request.REQUEST:
        apps = apps.filter(state=request.GET['state'])

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(created_by__short_name__icontains=term) | Q(created_by__full_name__icontains=term)
            query = query & q

        apps = apps.filter(query)
    else:
        terms = ""

    filter_list = []
    filter_list.append(Filter(request, 'state', Application.APPLICATION_STATES))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(apps, 50)

    try:
        page = p.page(page_no)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)

    return render_to_response(
            'applications/application_list_for_admin.html',
            {'page': page, 'filter_bar': filter_bar, 'terms': terms},
            context_instance=RequestContext(request))


@admin_required
def applicant_edit(request, applicant_id):
    
    applicant = get_object_or_404(Applicant, id=applicant_id)

    form = ApplicantForm(request.POST or None, instance=applicant)
    if request.method == 'POST':
        if form.is_valid():
            applicant = form.save()
            log(request.user, applicant, 2, 'Edited')
            messages.success(request, "%s modified successfully." % applicant)
            return HttpResponseRedirect(reverse('kg_application_list'))

    return render_to_response('applications/applicant_form.html',
            {'form': form}, context_instance=RequestContext(request))


@admin_required
def new_application(request):
    return render_to_response('applications/application_invite_admin.html',
            {},
            context_instance=RequestContext(request))


@admin_required
def application_logs(request, application_id):
    obj = get_object_or_404(Application, pk=application_id)
    return util.log_list(request, "Applications", reverse("kg_application_list"), obj.pid, obj)


@admin_required
def add_comment(request, application_id):
    obj = get_object_or_404(Application, pk=application_id)
    return util.add_comment(request, "Applications", reverse("kg_application_list"), obj.pid, obj)


