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
from django.core.paginator import Paginator
from django.conf import settings

from andsome.util.filterspecs import Filter, FilterBar

from karaage.util.graphs import get_institute_trend_graph_url
from karaage.people.models import Institute


def institute_detail(request, institute_id):
    
    institute = get_object_or_404(Institute, pk=institute_id)

    if institute.is_active:
        graph = get_institute_trend_graph_url(institute)
    
    return render_to_response('institutes/institute_detail.html', locals(), context_instance=RequestContext(request))
    

def institute_list(request):

    institute_list = Institute.objects.all()
    page_no = int(request.GET.get('page', 1))

    if request.REQUEST.has_key('active'):
        institute_list = institute_list.filter(is_active=int(request.GET['active']))

    filter_list = []
    filter_list.append(Filter(request, 'active', {1: 'Yes', 0: 'No'}))
    filter_bar = FilterBar(request, filter_list)

    p = Paginator(institute_list, 50)
    page = p.page(page_no)

    return render_to_response('institutes/institute_list.html', locals(), context_instance=RequestContext(request))

