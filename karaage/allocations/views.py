from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse

from karaage.common.decorators import admin_required, login_required

from karaage.allocations.forms import (
    AllocationForm,
    AllocationPeriodForm,
    GrantForm,
    SchemeForm,
)


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


    if request.method == "POST":
        form = AllocationForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation_list'))
            # The line below is just for testing that the view works
            return HttpResponse('Allocation set!')
    else:
        form = AllocationForm()

    return render(
        request,
        'karaage/allocations/allocation_add_template.html',
        {
            'form': form,
            'title': 'Add allocation',
        },
    )


@admin_required
def grant_add(request):

    if request.method == "POST":
        form = GrantForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation_list'))
            # The line below is just for testing that the view works
            return HttpResponse('Grant set!')
    else:
        form = GrantForm()

    return render(
        request,
        'karaage/allocations/allocation_add_template.html',
        {
            'form': form,
            'title': 'Add grant',
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
