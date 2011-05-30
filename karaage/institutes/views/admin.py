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
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.forms.models import inlineformset_factory

from andsome.util.filterspecs import Filter, FilterBar

from karaage.util.graphs import get_institute_trend_graph_url
from karaage.people.models import Institute, InstituteDelegate
from karaage.institutes.forms import InstituteForm

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


@permission_required('people.add_institute')
def add_edit_institute(request, institute_id=None):

    if institute_id:
        institute = get_object_or_404(Institute, pk=institute_id)
        flag = 2
    else:
        institute = None
        flag = 1

    DelegateFormSet = inlineformset_factory(Institute, InstituteDelegate, extra=3)

    if request.method == 'POST':
        form = InstituteForm(request.POST, instance=institute)
        delegate_formset = DelegateFormSet(request.POST, instance=institute)

        if form.is_valid() and delegate_formset.is_valid():
            institute = form.save()
            if flag == 1:
                delegate_formset = DelegateFormSet(request.POST, instance=institute)
                delegate_formset.is_valid()
            delegate_formset.save()
            return HttpResponseRedirect(institute.get_absolute_url())
    else:
        form = InstituteForm(instance=institute)
        delegate_formset = DelegateFormSet(instance=institute)

    return render_to_response(
        'institutes/institute_form.html', 
        {'institute': institute, 'form': form, 'delegate_formset': delegate_formset}, 
        context_instance=RequestContext(request))
