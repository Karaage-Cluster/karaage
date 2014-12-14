import six

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse

from karaage.common.decorators import admin_required, login_required
from karaage.allocations.models import AllocationPool
from karaage.allocations.forms import AllocationPeriodForm


@admin_required
def allocation_period(request, allocation_pool_id):

    allocation_pool = get_object_or_404(AllocationPool, id=allocation_pool_id)

    # TODO: Restrict this view only to authorised users
    # if not allocation_pool.can_view(request):
    #     return HttpResponseForbidden('<h1>Access Denied</h1>')

    if request.method == "POST":
        form = AllocationPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(reverse('allocation-period-list'))
            # The line below is just for testing that the view works
            return HttpResponse('Allocation period set!')
    else:
        form = AllocationPeriodForm()

    return render(
        'karaage/allocations/add_allocation_period.html',
        {
            'form': form,
        },
    )
