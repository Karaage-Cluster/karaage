from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)

from karaage.common.decorators import admin_required

from karaage.machines.models import (
    Resource,
    ResourcePool,
)
from karaage.machines.forms import (
    ResourceForm,
    ResourcePoolForm,
)


@admin_required
def add_edit_resource(request, resource_id=None):

    kwargs = {}

    if resource_id:
        mode = 'edit'
        title = 'Edit resource'
        kwargs['instance'] = Resource.objects.get(pk=resource_id)
    else:
        mode = 'add'
        title = 'Add resource'

    if request.method == "POST":
        kwargs['data'] = request.POST

    form = ResourceForm(**kwargs)

    if form.is_valid():
        form.save()
        return redirect('kg_machine_category_list')

    return render(
        request,
        'karaage/machines/resource_add_edit_template.html',
        {
            'mode': mode,
            'record_type': 'resource',
            'record_id': resource_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def delete_resource(request, resource_id):

    record = get_object_or_404(Resource, pk=resource_id)

    # TODO: Check for aggregate usage before deleting a resource

    if request.method == 'POST':
        record.delete()
        return redirect('kg_machine_category_list')

    return render(
        request,
        'karaage/machines/resource_confirm_delete_template.html',
        {
            'record': record,
            'record_type': 'resource',
        },
    )


@admin_required
def add_edit_resource_pool(request, resource_pool_id=None):

    kwargs = {}

    if resource_pool_id:
        mode = 'edit'
        title = 'Edit resource pool'
        kwargs['instance'] = ResourcePool.objects.get(pk=resource_pool_id)
    else:
        mode = 'add'
        title = 'Add resource pool'

    if request.method == "POST":
        kwargs['data'] = request.POST

    form = ResourcePoolForm(**kwargs)

    if form.is_valid():
        form.save()
        return redirect('kg_machine_category_list')

    return render(
        request,
        'karaage/machines/resource_add_edit_template.html',
        {
            'mode': mode,
            'record_type': 'resource pool',
            'record_id': resource_pool_id,
            'form': form,
            'title': title,
        },
    )


@admin_required
def delete_resource_pool(request, resource_pool_id):

    record = get_object_or_404(ResourcePool, pk=resource_pool_id)

    errors = []
    # TODO: Check for aggregate usage before deleting a resource pool
    for child in record.resource_set.all():
        errors.append(
            'Resource "%s" depends on this resource pool.' % child

        )
    for child in record.allocationpool_set.all():
        errors.append(
            'Allocation pool "%s" depends on this resource pool.' % child
        )

    if request.method == 'POST':
        record.delete()
        return redirect('kg_machine_category_list')

    return render(
        request,
        'karaage/machines/resource_confirm_delete_template.html',
        {
            'record': record,
            'record_type': 'resource_pool',
            'errors': errors,
        },
    )
