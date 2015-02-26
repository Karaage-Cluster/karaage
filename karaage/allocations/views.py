# Copyright 2014 The University of Melbourne
# Copyright 2015 VPAC
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

from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)

from karaage.allocations.models import (
    Allocation,
    AllocationPool,
    Grant,
)
from karaage.allocations.forms import (
    AllocationForm,
    AllocationPeriodForm,
    GrantForm,
    SchemeForm,
)
from karaage.common.models import Usage
from karaage.common.decorators import admin_required
from karaage.projects.models import Project


@admin_required
def allocation_period_add(request, project_id):

    project = Project.objects.get(pk=project_id)

    if request.method == "POST":
        form = AllocationPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kg_project_detail', project_id)
    else:
        form = AllocationPeriodForm()

    return render(
        request,
        'karaage/allocations/allocation_add_edit_template.html',
        {
            'project': project,
            'form': form,
            'title': 'Add allocation period',
        },
    )


@admin_required
def add_edit_allocation(request, project_id, allocation_id=None):

    project = Project.objects.get(pk=project_id)

    kwargs = {
        'project': project,
    }

    if allocation_id:
        mode = 'edit'
        title = 'Edit allocation'
        kwargs['instance'] = alloc = Allocation.objects.get(pk=allocation_id)
        kwargs['initial'] = {
            'period': alloc.allocation_pool.period,
            'resource_pool': alloc.allocation_pool.resource_pool,
        }
    else:
        mode = 'add'
        title = 'Add allocation'

    if request.method == "POST":
        kwargs['data'] = request.POST

    form = AllocationForm(**kwargs)

    # TODO: Need to periodically clean up allocation pools which have
    # had all their allocations removed
    if form.is_valid():
        alloc = form.save(commit=False)
        obj, created = AllocationPool.objects.get_or_create(
            project=project,
            period=form.cleaned_data['period'],
            resource_pool=form.cleaned_data['resource_pool'],
        )
        alloc.allocation_pool = obj
        alloc.save()
        return redirect('kg_project_detail', project_id)

    return render(
        request,
        'karaage/allocations/allocation_add_edit_template.html',
        {
            'mode': mode,
            'record_type': 'allocation',
            'project': project,
            'record_id': allocation_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def delete_allocation(request, project_id, allocation_id):

    project = Project.objects.get(pk=project_id)
    record = get_object_or_404(Allocation, pk=allocation_id)

    if request.method == 'POST':
        record.delete()
        return redirect('kg_project_detail', project_id)

    return render(
        request,
        'karaage/allocations/allocation_confirm_delete_template.html',
        {
            'project': project,
            'record': record,
            'record_type': 'allocation',
        },
    )


@admin_required
def add_edit_grant(request, project_id, grant_id=None):

    project = Project.objects.get(pk=project_id)

    if grant_id:
        mode = 'edit'
        title = 'Edit grant'
        grant = Grant.objects.get(pk=grant_id)
    else:
        mode = 'add'
        title = 'Add grant'

    if request.method == "POST":
        if grant_id:
            form = GrantForm(request.POST, instance=grant)
        else:
            form = GrantForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.project = project
            obj.save()
            return redirect('kg_project_detail', project_id)
    else:
        if grant_id:
            form = GrantForm(instance=grant)
        else:
            form = GrantForm()

    return render(
        request,
        'karaage/allocations/allocation_add_edit_template.html',
        {
            'mode': mode,
            'record_type': 'grant',
            'project': project,
            'record_id': grant_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def delete_grant(request, project_id, grant_id):

    project = Project.objects.get(pk=project_id)

    record = get_object_or_404(Grant, pk=grant_id)
    record_type = 'grant'

    errors = []
    if Allocation.objects.filter(grant=record).exists():
        errors.append('At least one allocation is using this grant')
    if Usage.objects.filter(grant=record).exists():
        errors.append(
            'At least one usage record table record references this grant'
        )

    if request.method == 'POST':
        record.delete()
        return redirect('kg_project_detail', project_id)

    return render(
        request,
        'karaage/allocations/allocation_confirm_delete_template.html',
        {
            'project': project,
            'record': record,
            'record_type': record_type,
            'errors': errors,
        },
    )


@admin_required
def scheme_add(request, project_id):

    project = Project.objects.get(pk=project_id)

    if request.method == "POST":
        form = SchemeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kg_project_detail', project_id)
    else:
        form = SchemeForm()

    return render(
        request,
        'karaage/allocations/allocation_add_edit_template.html',
        {
            'project': project,
            'form': form,
            'title': 'Add scheme',
        },
    )
