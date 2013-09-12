# Copyright 2007-2013 VPAC
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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from karaage.machines.models import Machine, MachineCategory
from karaage.util.decorators import admin_required

@admin_required
def index(request):
    category_list = MachineCategory.objects.all()
    return render_to_response(
        'machines/machine_list.html',
        {'category_list': category_list},
        context_instance=RequestContext(request))


@admin_required
def machine_detail(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    usage_list = machine.cpujob_set.all()[:5]
    return render_to_response(
        'machines/machine_detail.html',
        {'machine': machine, 'usage_list': usage_list},
        context_instance=RequestContext(request))

@admin_required
def machine_create(request):
    from karaage.legacy.create_update import create_object
    return create_object(request,
            model=Machine)

@admin_required
def machine_edit(request, machine_id):
    from karaage.legacy.create_update import update_object
    return update_object(request,
            object_id=machine_id, model=Machine)

@admin_required
def machine_accounts(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    accounts = machine.category.account_set.filter(date_deleted__isnull=True)
    return render_to_response(
        'machines/machine_accounts.html',
        {'machine': machine, 'accounts': accounts},
        context_instance=RequestContext(request))

@admin_required
def machine_projects(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    project_list = machine.category.projects.all()
    return render_to_response(
        'machines/machine_projects.html',
        {'machine': machine, 'project_list': project_list},
        context_instance=RequestContext(request))


@admin_required
def category_create(request):
    from karaage.legacy.create_update import create_object
    return create_object(request,
            model=MachineCategory)

@admin_required
def category_edit(request, category_id):
    from karaage.legacy.create_update import update_object
    return update_object(request,
            object_id=category_id, model=MachineCategory)

