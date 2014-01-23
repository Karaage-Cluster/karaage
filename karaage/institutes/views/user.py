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
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator

from karaage.common.filterspecs import Filter, FilterBar
from karaage.common.decorators import login_required
from karaage.institutes.models import Institute

@login_required
def institute_list(request):

    institute_list = Institute.objects.filter(delegates=request.user)
    page_no = int(request.GET.get('page', 1))

    if 'active' in request.REQUEST:
        institute_list = institute_list.filter(is_active=int(request.GET['active']))

    terms = ""
    if 'search' in request.REQUEST:
        institute_list = institute_list.filter(name__icontains=request.GET['search'])
        terms = request.GET['search']

    filter_list = []
    filter_list.append(Filter(request, 'active', {1: 'Yes', 0: 'No'}))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(institute_list, 50)
    page = p.page(page_no)

    return render_to_response('institutes/institute_list.html', locals(), context_instance=RequestContext(request))

@login_required
def institute_detail(request, institute_id):
    institute = get_object_or_404(Institute, pk=institute_id)

    if not request.user in institute.delegates.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    return render_to_response('institutes/institute_detail.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_users_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    if not request.user in institute.delegates.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    user_list = institute.person_set.select_related()

    return render_to_response('institutes/institute_user_list.html', locals(), context_instance=RequestContext(request))


@login_required
def institute_projects_list(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    if not request.user in institute.delegates.all():
        return HttpResponseForbidden('<h1>Access Denied</h1>')

    project_list = institute.project_set.select_related()

    return render_to_response('institutes/institute_projects_list.html', locals(), context_instance=RequestContext(request))
