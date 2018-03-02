# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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
import six
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import karaage.common as util
from karaage.common import is_admin
from karaage.common.decorators import admin_required, login_required
from karaage.institutes.forms import DelegateForm, InstituteForm
from karaage.institutes.models import Institute, InstituteDelegate
from karaage.institutes.tables import InstituteFilter, InstituteTable
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

    return render(
        template_name='karaage/institutes/profile_institutes.html',
        context={
            'person': person,
            'my_institute_list': my_institute_list,
            'delegate_institute_list': delegate_institute_list},
        request=request)


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

    return render(
        template_name='karaage/institutes/institute_detail.html',
        context=locals(),
        request=request)


@admin_required
def institute_verbose(request, institute_id):
    institute = get_object_or_404(Institute, pk=institute_id)

    from karaage.datastores import get_institute_details
    institute_details = get_institute_details(institute)

    return render(
        template_name='karaage/institutes/institute_verbose.html',
        context=locals(),
        request=request)


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

    return render(
        template_name='karaage/institutes/institute_list.html',
        context={
            'table': table,
            'filter': q_filter,
            'spec': spec,
            'title': "Institute list",
        },
        request=request)


@admin_required
def add_edit_institute(request, institute_id=None):

    if institute_id:
        institute = get_object_or_404(Institute, pk=institute_id)
    else:
        institute = None

    delegate_formset_class = inlineformset_factory(
        Institute, InstituteDelegate, form=DelegateForm, extra=3,
        min_num=1, validate_min=True)

    if request.method == 'POST':
        form = InstituteForm(request.POST, instance=institute)

        delegate_formset = delegate_formset_class(
            request.POST, instance=institute)

        if form.is_valid():
            institute = form.save()

            if delegate_formset.is_valid():
                delegate_formset.save()
                return HttpResponseRedirect(institute.get_absolute_url())
    else:
        form = InstituteForm(instance=institute)
        delegate_formset = delegate_formset_class(instance=institute)

    media = form.media
    for dform in delegate_formset.forms:
        media = media + dform.media

    return render(
        template_name='karaage/institutes/institute_form.html',
        context={
            'institute': institute, 'form': form,
            'media': media, 'delegate_formset': delegate_formset},
        request=request)


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
