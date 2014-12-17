from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)

from karaage.allocations.models import (
    Allocation,
    Grant,
)
from karaage.allocations.forms import (
    AllocationForm,
    AllocationPeriodForm,
    GrantForm,
    SchemeForm,
)
from karaage.common.decorators import admin_required, login_required
from karaage.projects.models import Project


@admin_required
def allocation_period_add(request):

    if request.method == "POST":
        form = AllocationPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation_list'))
            # The line below is just for testing that the view works
            return HttpResponse('Allocation period set!')
    else:
        form = AllocationPeriodForm()

    return render(
        request,
        'karaage/allocations/allocation_add_template.html',
        {
            'form': form,
            'title': 'Add allocation period',
        },
    )


@admin_required
def add_edit_allocation(request, project_id, allocation_id=None):

    project = Project.objects.get(pk=project_id)

    if allocation_id:
        title = 'Edit allocation'
        allocation = Allocation.objects.get(pk=allocation_id)
    else:
        title = 'Add allocation'

    if request.method == "POST":
        if allocation_id:
            form = AllocationForm(project, request.POST, instance=allocation)
        else:
            form = AllocationForm(project, request.POST)
        if form.is_valid():
            form.save()
            return redirect('kg_project_detail', project_id)
    else:
        if allocation_id:
            form = AllocationForm(project, instance=allocation)
        else:
            form = AllocationForm(project)

    return render(
        request,
        'karaage/allocations/allocation_add_edit_template.html',
        {
            'pid': project_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def add_edit_grant(request, project_id, grant_id=None):

    project = Project.objects.get(pk=project_id)

    if grant_id:
        title = 'Edit grant'
        grant = Grant.objects.get(pk=grant_id)
    else:
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
            'pid': project_id,
            'form': form,
            'title': title,
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
