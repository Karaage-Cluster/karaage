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

import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.forms.models import inlineformset_factory

from andsome.util.filterspecs import Filter, FilterBar

from karaage.common.decorators import admin_required
import karaage.common as util
from karaage.usage.graphs import get_institute_trend_graph_url
from karaage.institutes.models import Institute, InstituteQuota, InstituteDelegate
from karaage.institutes.forms import InstituteForm, InstituteQuotaForm, DelegateForm
from karaage.machines.models import MachineCategory


@admin_required
def institute_detail(request, institute_id):
    
    institute = get_object_or_404(Institute, pk=institute_id)

    start=datetime.date.today() - datetime.timedelta(days=90)
    end=datetime.date.today()

    if institute.is_active:
        graph = {}
        for ic in institute.institutequota_set.all():
            graph[ic.machine_category] = get_institute_trend_graph_url(institute, start, end, ic.machine_category)
    
    return render_to_response('institutes/institute_detail.html', locals(), context_instance=RequestContext(request))
    

@admin_required
def institute_verbose(request, institute_id):
    institute = get_object_or_404(Institute, pk=institute_id)

    from karaage.datastores import get_institute_details
    institute_details = get_institute_details(institute)

    return render_to_response('institutes/institute_verbose.html', locals(), context_instance=RequestContext(request))


@admin_required
def institute_list(request):

    institute_list = Institute.objects.all()
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


@admin_required
def add_edit_institute(request, institute_id=None):

    if institute_id:
        institute = get_object_or_404(Institute, pk=institute_id)
        flag = 2
    else:
        institute = None
        flag = 1

    DelegateFormSet = inlineformset_factory(Institute, InstituteDelegate, form=DelegateForm, extra=3)

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

@admin_required
def institute_quota_edit(request, institutequota_id):
    from karaage.legacy.create_update import update_object
    return update_object(request,
            object_id=institutequota_id, model=InstituteQuota)


@admin_required
def institutequota_add(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)

    institute_chunk = InstituteQuota()
    institute_chunk.institute = institute

    form = InstituteQuotaForm(request.POST or None, instance=institute_chunk)
    if request.method == 'POST':
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            conflicting = InstituteQuota.objects.filter(
                institute=institute,machine_category=mc)

            if conflicting.count() >= 1:
                form._errors["machine_category"] = util.ErrorList(["Cap already exists with this machine category"])
            else:
                institute_chunk = form.save()
                new_cap = institute_chunk.cap
                log(request.user, institute, 2, 'Added cap of %s' % (new_cap))
                return HttpResponseRedirect(institute.get_absolute_url())

    return render_to_response('institutes/institutequota_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def institutequota_edit(request, institutequota_id):

    institute_chunk = get_object_or_404(InstituteQuota, pk=institutequota_id)
    old_cap = institute_chunk.cap
    old_mc = institute_chunk.machine_category

    form = InstituteQuotaForm(request.POST or None, instance=institute_chunk)
    if request.method == 'POST':
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            if old_mc.pk != mc.pk:
                form._errors["machine_category"] = util.ErrorList(["Please don't change the machine category; it confuses me"])
            else:
                institute_chunk = form.save()
                new_cap = institute_chunk.cap
                if old_cap != new_cap:
                    log(request.user, institute_chunk.institute, 2, 'Changed cap from %s to %s' % (old_cap, new_cap))
                return HttpResponseRedirect(institute_chunk.institute.get_absolute_url())

    return render_to_response('institutes/institutequota_form.html', locals(), context_instance=RequestContext(request))


@admin_required
def institutequota_delete(request, institutequota_id):

    institute_chunk = get_object_or_404(InstituteQuota, pk=institutequota_id)

    if request.method == 'POST':
        institute_chunk.delete()
        return HttpResponseRedirect(institute_chunk.institute.get_absolute_url())

    return render_to_response('institutes/institutequota_delete_form.html', locals(), context_instance=RequestContext(request))

@admin_required
def projects_by_cap_used(request):
    from karaage.projects.views.admin import project_list
    return project_list(request, queryset=Project.active.all(), paginate=False, template_name='pbsmoab/project_capsort.html')
    
    
def institute_logs(request, institute_id):
    obj = get_object_or_404(Institute, pk=institute_id)
    return util.log_list(request, "Institutes", reverse("kg_institute_list"), unicode(obj), obj)


@admin_required
def add_comment(request, institute_id):
    obj = get_object_or_404(Institute, pk=institute_id)
    return util.add_comment(request, "Institutes", reverse("kg_institute_list"), unicode(obj), obj)
