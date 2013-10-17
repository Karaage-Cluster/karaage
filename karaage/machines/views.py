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

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from karaage.projects.models import Project
from karaage.machines.models import Machine, MachineCategory
from karaage.common.decorators import admin_required
import karaage.common as util

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
def machine_password(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    password = None
    if request.method == 'POST':
        password = Machine.objects.make_random_password()
        machine.set_password(password)
        machine.save()
    return render_to_response(
        'machines/machine_password.html',
        {'machine': machine, 'password': password},
        context_instance=RequestContext(request))

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
    project_list = Project.objects.filter(projectquota__machine_category=machine.category)
    return render_to_response(
        'machines/machine_projects.html',
        {'machine': machine, 'project_list': project_list},
        context_instance=RequestContext(request))


@admin_required
def machine_logs(request, machine_id):
    obj = get_object_or_404(Machine, pk=machine_id)
    breadcrumbs = []
    breadcrumbs.append( ("Machines", reverse("kg_machine_list")) )
    breadcrumbs.append( (unicode(obj.category), reverse("kg_machine_category_detail", args=[obj.category.pk])) )
    breadcrumbs.append( (unicode(obj), reverse("kg_machine_detail", args=[obj.pk])) )
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def machine_add_comment(request, machine_id):
    obj = get_object_or_404(Machine, pk=machine_id)
    breadcrumbs = []
    breadcrumbs.append( ("Machines", reverse("kg_machine_list")) )
    breadcrumbs.append( (unicode(obj.category), reverse("kg_machine_category_detail", args=[obj.category.pk])) )
    breadcrumbs.append( (unicode(obj), reverse("kg_machine_detail", args=[obj.pk])) )
    return util.add_comment(request, breadcrumbs, obj)


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

@admin_required
def category_detail(request, category_id):
    machine_category = get_object_or_404(MachineCategory, pk=category_id)
    return render_to_response(
        'machines/machinecategory_detail.html',
        {'machine_category': machine_category, },
        context_instance=RequestContext(request))


@admin_required
def category_logs(request, category_id):
    obj = get_object_or_404(MachineCategory, pk=category_id)
    breadcrumbs = []
    breadcrumbs.append( ("Machines", reverse("kg_machine_list")) )
    breadcrumbs.append( (unicode(obj), reverse("kg_machine_category_detail", args=[obj.pk])) )
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def category_add_comment(request, category_id):
    obj = get_object_or_404(MachineCategory, pk=category_id)
    breadcrumbs = []
    breadcrumbs.append( ("Machines", reverse("kg_machine_list")) )
    breadcrumbs.append( (unicode(obj), reverse("kg_machine_category_detail", args=[obj.pk])) )
    return util.add_comment(request, breadcrumbs, obj)

