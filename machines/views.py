from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.decorators import permission_required

from karaage.people.models import Institute

from forms import MachineForm
from models import Machine, MachineCategory

def index(request):

    category_list = MachineCategory.objects.all()

    return render_to_response('machines/machine_list.html', locals(), context_instance=RequestContext(request))


def machine_detail(request, machine_id):

    machine = get_object_or_404(Machine, pk=machine_id)

    usage_list = machine.cpujob_set.all()[:5]

    return render_to_response('machines/machine_detail.html', locals(), context_instance=RequestContext(request))


def add_edit_machine(request, machine_id=None):
    if machine_id is None:
        m = None
    else:
        m = get_object_or_404(Machine, pk=machine_id)

    if request.method == 'POST':
        form = MachineForm(request.POST, m)
        if form.is_valid():
            m = form.save()
            return HttpResponseRedirect(m.get_absolute_url())
    else:
        form = MachineForm(m)
    return render_to_response('machines/machine_form.html', locals(), context_instance=RequestContext(request))

add_edit_machine = permission_required('main.add_machine')(add_edit_machine)


def machine_accounts(request, machine_id):

    machine = get_object_or_404(Machine, pk=machine_id)
    user_accounts = machine.category.useraccount_set.filter(date_deleted__isnull=True).select_related().order_by('auth_user.first_name', 'auth_user.last_name')

    return render_to_response('machines/machine_accounts.html', locals(), context_instance=RequestContext(request))


def machine_projects(request, machine_id):

    machine = get_object_or_404(Machine, pk=machine_id)
    project_list = machine.category.project_set.all()

    return render_to_response('machines/machine_projects.html', locals(), context_instance=RequestContext(request))
