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
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from andsome.util.filterspecs import Filter, FilterBar

from karaage.applications.models import Applicant, Application
from karaage.applications.forms import ApplicantForm
from karaage.util import log_object as log


@login_required
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
            q = Q(created_by__first_name__icontains=term) | Q(created_by__last_name__icontains=term)
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


@permission_required('applications.change_applicant')
def applicant_edit(request, applicant_id):
    
    applicant = get_object_or_404(Applicant, id=applicant_id)

    if request.method == 'POST':
        form = ApplicantForm(request.POST, instance=applicant)
        if form.is_valid():
            applicant = form.save()
            log(request.user, applicant, 2, 'Edited')
            messages.success(request, "%s modified successfully." % applicant)
            try:
                return HttpResponseRedirect(applicant.applications.all()[0].get_absolute_url())
            except IndexError:
                return HttpResponseRedirect(reverse('kg_application_list'))
    else:
        form = ApplicantForm(instance=applicant)
    
    return render_to_response('applications/applicant_form.html', {'applicant': applicant, 'form': form}, context_instance=RequestContext(request))
