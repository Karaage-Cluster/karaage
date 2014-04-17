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

import django_tables2 as tables
from django_tables2.utils import A
import django_filters

from django.forms.util import ErrorList
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

from karaage.common import is_admin
from karaage.common.decorators import admin_required, login_required
import karaage.common as util
from karaage.people.tables import PeopleColumn
from karaage.institutes.models import Institute, InstituteQuota, \
    InstituteDelegate
from karaage.institutes.forms import InstituteForm, InstituteQuotaForm, \
    DelegateForm


class InstituteFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Institute
        fields = ('name', 'is_active')


class InstituteTable(tables.Table):
    name = tables.LinkColumn('kg_institute_detail', args=[A('pk')])
    delegates = PeopleColumn(orderable=False)

    class Meta:
        model = Institute
        fields = ('name', 'is_active')


@login_required
def profile_institutes(request):

    person = request.user
    institute_list = person.delegate_for.all()

    return render_to_response(
        'institutes/profile_institutes.html',
        {'person': person, 'institute_list': institute_list},
        context_instance=RequestContext(request))


@login_required
def institute_detail(request, institute_id):

    institute = get_object_or_404(Institute, pk=institute_id)
    if not institute.can_view(request):
        return HttpResponseForbidden(
            '<h1>Access Denied</h1>'
            '<p>You do not have permission to view details'
            'about this institute.</p>')

    return render_to_response(
        'institutes/institute_detail.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def institute_verbose(request, institute_id):
    institute = get_object_or_404(Institute, pk=institute_id)

    from karaage.datastores import machine_category_get_institute_details
    institute_details = machine_category_get_institute_details(institute)

    return render_to_response(
        'institutes/institute_verbose.html',
        locals(),
        context_instance=RequestContext(request))


@login_required
def institute_list(request):

    queryset = Institute.objects.all()
    if not is_admin(request):
        queryset = institute_list.filter(
            is_active=True, delegates=request.user)

    filter = InstituteFilter(request.GET, queryset=queryset)
    table = InstituteTable(filter)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in filter.form.cleaned_data.iteritems():
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        'institutes/institute_list.html',
        {
            'table': table,
            'filter': filter,
            'spec': spec,
            'title': "Institute list",
        },
        context_instance=RequestContext(request))


@admin_required
def add_edit_institute(request, institute_id=None):

    if institute_id:
        institute = get_object_or_404(Institute, pk=institute_id)
        flag = 2
    else:
        institute = None
        flag = 1

    DelegateFormSet = inlineformset_factory(
        Institute, InstituteDelegate, form=DelegateForm, extra=3)

    if request.method == 'POST':
        form = InstituteForm(request.POST, instance=institute)
        delegate_formset = DelegateFormSet(request.POST, instance=institute)

        if form.is_valid() and delegate_formset.is_valid():
            institute = form.save()
            if flag == 1:
                delegate_formset = DelegateFormSet(
                    request.POST, instance=institute)
                delegate_formset.is_valid()
            delegate_formset.save()
            return HttpResponseRedirect(institute.get_absolute_url())
    else:
        form = InstituteForm(instance=institute)
        delegate_formset = DelegateFormSet(instance=institute)

    media = form.media
    for dform in delegate_formset.forms:
        media = media + dform.media

    return render_to_response(
        'institutes/institute_form.html',
        {'institute': institute, 'form': form,
            'media': media, 'delegate_formset': delegate_formset},
        context_instance=RequestContext(request))


@admin_required
def institute_quota_edit(request, institutequota_id):
    from karaage.common.create_update import update_object
    return update_object(
        request, object_id=institutequota_id, model=InstituteQuota)


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
                institute=institute, machine_category=mc)

            if conflicting.count() >= 1:
                form._errors["machine_category"] = \
                    ErrorList([
                        "Cap already exists with this machine category"])
            else:
                institute_chunk = form.save()
                return HttpResponseRedirect(institute.get_absolute_url())

    return render_to_response(
        'institutes/institutequota_form.html',
        {'form': form, 'institute': institute, },
        context_instance=RequestContext(request))


@admin_required
def institutequota_edit(request, institutequota_id):

    institute_chunk = get_object_or_404(InstituteQuota, pk=institutequota_id)
    old_mc = institute_chunk.machine_category

    form = InstituteQuotaForm(request.POST or None, instance=institute_chunk)
    if request.method == 'POST':
        if form.is_valid():
            mc = form.cleaned_data['machine_category']
            if old_mc.pk != mc.pk:
                form._errors["machine_category"] = \
                    ErrorList([
                        "Please don't change the machine category; "
                        "it confuses me"])
            else:
                institute_chunk = form.save()
                return HttpResponseRedirect(
                    institute_chunk.institute.get_absolute_url())

    return render_to_response(
        'institutes/institutequota_form.html',
        {'form': form, 'institute': institute_chunk.institute,
            'object': institute_chunk},
        context_instance=RequestContext(request))


@admin_required
def institutequota_delete(request, institutequota_id):

    institute_chunk = get_object_or_404(InstituteQuota, pk=institutequota_id)

    if request.method == 'POST':
        institute_chunk.delete()
        return HttpResponseRedirect(
            institute_chunk.institute.get_absolute_url())

    return render_to_response(
        'institutes/institutequota_delete_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def institute_logs(request, institute_id):
    obj = get_object_or_404(Institute, pk=institute_id)
    breadcrumbs = []
    breadcrumbs.append(
        ("Institutes", reverse("kg_institute_list")))
    breadcrumbs.append(
        (unicode(obj), reverse("kg_institute_detail", args=[obj.pk])))
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, institute_id):
    obj = get_object_or_404(Institute, pk=institute_id)
    breadcrumbs = []
    breadcrumbs.append(
        ("Institutes", reverse("kg_institute_list")))
    breadcrumbs.append(
        (unicode(obj), reverse("kg_institute_detail", args=[obj.pk])))
    return util.add_comment(request, breadcrumbs, obj)
