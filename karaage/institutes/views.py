# Copyright 2008-2011, 2013-2015 VPAC
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

import six
import django_tables2 as tables

from django.db.models import Q
from django.forms.utils import ErrorList
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

from karaage.common import is_admin
from karaage.common.decorators import admin_required, login_required
import karaage.common as util
from karaage.institutes.tables import InstituteTable, InstituteFilter
from karaage.institutes.models import Institute, InstituteQuota, \
    InstituteDelegate
from karaage.institutes.forms import InstituteForm, InstituteQuotaForm, \
    DelegateForm
from karaage.people.models import Person
from karaage.people.tables import PersonTable
from karaage.projects.tables import ProjectTable


@login_required
def profile_institutes(request):
    config = tables.RequestConfig(request, paginate={"per_page": 5})

    person = request.user

    my_institute_list = Institute.objects.filter(
        Q(pk=person.institute_id) | Q(group__members=person))
    my_institute_list = my_institute_list.select_related()
    my_institute_list = InstituteTable(my_institute_list, prefix="mine")
    config.configure(my_institute_list)

    delegate_institute_list = person.delegate_for.all()
    delegate_institute_list = delegate_institute_list.select_related()
    delegate_institute_list = InstituteTable(
        delegate_institute_list, prefix="delegate")
    config.configure(delegate_institute_list)

    return render_to_response(
        'karaage/institutes/profile_institutes.html',
        {'person': person,
            'my_institute_list': my_institute_list,
            'delegate_institute_list': delegate_institute_list},
        context_instance=RequestContext(request))


@login_required
def institute_detail(request, institute_id):
    config = tables.RequestConfig(request, paginate={"per_page": 5})

    institute = get_object_or_404(Institute, pk=institute_id)
    if not institute.can_view(request):
        return HttpResponseForbidden(
            '<h1>Access Denied</h1>'
            '<p>You do not have permission to view details'
            'about this institute.</p>')

    project_list = institute.project_set.select_related()
    project_list = ProjectTable(project_list, prefix="project-")
    config.configure(project_list)

    person_list = Person.objects.filter(
        Q(institute__pk=institute_id) | Q(groups__institute=institute_id))
    person_list = person_list.select_related()
    person_list = PersonTable(person_list, prefix="person-")
    config.configure(person_list)

    return render_to_response(
        'karaage/institutes/institute_detail.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def institute_verbose(request, institute_id):
    institute = get_object_or_404(Institute, pk=institute_id)

    from karaage.datastores import machine_category_get_institute_details
    institute_details = machine_category_get_institute_details(institute)

    return render_to_response(
        'karaage/institutes/institute_verbose.html',
        locals(),
        context_instance=RequestContext(request))


@login_required
def institute_list(request):

    queryset = Institute.objects.all()
    if not is_admin(request):
        queryset = institute_list.filter(
            is_active=True, delegates=request.user)

    q_filter = InstituteFilter(request.GET, queryset=queryset)
    table = InstituteTable(q_filter.qs)
    tables.RequestConfig(request).configure(table)

    spec = []
    for name, value in six.iteritems(q_filter.form.cleaned_data):
        if value is not None and value != "":
            name = name.replace('_', ' ').capitalize()
            spec.append((name, value))

    return render_to_response(
        'karaage/institutes/institute_list.html',
        {
            'table': table,
            'filter': q_filter,
            'spec': spec,
            'title': "Institute list",
        },
        context_instance=RequestContext(request))


@admin_required
def add_edit_institute(request, institute_id=None):

    if institute_id:
        institute = get_object_or_404(Institute, pk=institute_id)
    else:
        institute = None

    delegate_formset_class = inlineformset_factory(
        Institute, InstituteDelegate, form=DelegateForm, extra=3)

    if request.method == 'POST':
        form = InstituteForm(request.POST, instance=institute)

        if form.is_valid():
            institute = form.save()

            delegate_formset = delegate_formset_class(
                request.POST, instance=institute)

            if delegate_formset.is_valid():
                delegate_formset.save()
                return HttpResponseRedirect(institute.get_absolute_url())
    else:
        form = InstituteForm(instance=institute)
        delegate_formset = delegate_formset_class(instance=institute)

    media = form.media
    for dform in delegate_formset.forms:
        media = media + dform.media

    return render_to_response(
        'karaage/institutes/institute_form.html',
        {'institute': institute, 'form': form,
            'media': media, 'delegate_formset': delegate_formset},
        context_instance=RequestContext(request))


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
        'karaage/institutes/institutequota_form.html',
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
        'karaage/institutes/institutequota_form.html',
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
        'karaage/institutes/institutequota_delete_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def institute_logs(request, institute_id):
    obj = get_object_or_404(Institute, pk=institute_id)
    breadcrumbs = [
        ("Institutes", reverse("kg_institute_list")),
        (six.text_type(obj), reverse("kg_institute_detail", args=[obj.pk]))
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def add_comment(request, institute_id):
    obj = get_object_or_404(Institute, pk=institute_id)
    breadcrumbs = [
        ("Institutes", reverse("kg_institute_list")),
        (six.text_type(obj), reverse("kg_institute_detail", args=[obj.pk]))
    ]
    return util.add_comment(request, breadcrumbs, obj)
