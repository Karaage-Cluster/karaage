from django.http import HttpResponse
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
from karaage.allocations.utils import create_allocation_pool_if_required
from karaage.common.models import Usage
from karaage.common.decorators import admin_required, login_required
from karaage.projects.models import Project


@admin_required
def allocation_period_add(request, project_id):

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
            'pid': project_id,
            'form': form,
            'title': 'Add allocation period',
        },
    )


@admin_required
def add_edit_allocation(request, project_id, allocation_id=None):

    kwargs = {
        'project': Project.objects.get(pk=project_id),
    }

    if allocation_id:
        mode = 'edit'
        title = 'Edit allocation'
        kwargs['instance'] = Allocation.objects.get(pk=allocation_id)
    else:
        mode = 'add'
        title = 'Add allocation'

    if request.method == "POST":
        kwargs['data'] = request.POST

    form = AllocationForm(**kwargs)

    if form.is_valid():
        alloc = form.save(commit=False)
        obj, created = AllocationPool.objects.get_or_create(
            project=kwargs['project'],
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
            'pid': project_id,
            'record_id': allocation_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def delete_allocation(request, project_id, allocation_id):

    record = get_object_or_404(Allocation, pk=allocation_id)

    if request.method == 'POST':
        record.delete()
        return redirect('kg_project_detail', project_id)

    return render(
        request,
        'karaage/allocations/allocation_confirm_delete_template.html',
        {
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
            'pid': project_id,
            'record_id': grant_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def delete_grant(request, project_id, grant_id):

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
            'record': record,
            'record_type': record_type,
            'errors': errors,
        },
    )


@admin_required
def scheme_add(request):

    if request.method == "POST":
        form = SchemeForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation_list'))
            # The line below is just for testing that the view works
            return HttpResponse('Scheme set!')
    else:
        form = SchemeForm()

    return render(
        request,
        'karaage/allocations/allocation_add_template.html',
        {
            'form': form,
            'title': 'Add scheme',
        },
    )
