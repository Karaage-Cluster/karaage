from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse

from karaage.common.decorators import admin_required, login_required

from karaage.machines.forms import (
    ResourceForm,
    ResourcePoolForm,
)


# TODO: Restrict this view only to authorised users
# @admin_required
def resource_add(request):

    # if not allocation_pool.can_view(request):
    #     return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == "POST":
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation_list'))
            # The line below is just for testing that the view works
            return HttpResponse('Resource created!')
    else:
        form = ResourceForm()

    return render(
        request,
        'karaage/machines/resource_add.html',
        {
            'form': form,
        },
    )


# TODO: Restrict this view only to authorised users
# @admin_required
def resource_pool_add(request):

    # if not allocation_pool.can_view(request):
    #     return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == "POST":
        form = ResourcePoolForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation_list'))
            # The line below is just for testing that the view works
            return HttpResponse('Resource pool created!')
    else:
        form = ResourcePoolForm()

    return render(
        request,
        'karaage/machines/resource_pool_add.html',
        {
            'form': form,
        },
    )
