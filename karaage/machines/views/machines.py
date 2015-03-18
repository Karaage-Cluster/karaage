# Copyright 2008, 2010-2015 VPAC
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

import six
import django_tables2 as tables

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from karaage.projects.tables import ProjectTable
from karaage.projects.models import Project
from karaage.machines.tables import MachineTable, MachineCategoryTable
from karaage.machines.tables import AccountTable
from karaage.machines.models import Machine, MachineCategory
from karaage.machines.forms import MachineForm, MachineCategoryForm
from karaage.common.decorators import admin_required, login_required
import karaage.common as util


@login_required
def machine_detail(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    return render_to_response(
        'karaage/machines/machine_detail.html',
        {'machine': machine},
        context_instance=RequestContext(request))


@admin_required
def machine_create(request):
    form = MachineForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            machine = form.save()
            return HttpResponseRedirect(machine.get_absolute_url())

    return render_to_response(
        'karaage/machines/machine_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def machine_edit(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)

    form = MachineForm(request.POST or None, instance=machine)
    if request.method == 'POST':
        if form.is_valid():
            machine = form.save()
            return HttpResponseRedirect(machine.get_absolute_url())

    return render_to_response(
        'karaage/machines/machine_form.html',
        locals(),
        context_instance=RequestContext(request))


@admin_required
def machine_password(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    password = None
    if request.method == 'POST':
        password = Machine.objects.make_random_password()
        machine.set_password(password)
        machine.save()
    return render_to_response(
        'karaage/machines/machine_password.html',
        {'machine': machine, 'password': password},
        context_instance=RequestContext(request))


@admin_required
def machine_logs(request, machine_id):
    obj = get_object_or_404(Machine, pk=machine_id)
    breadcrumbs = [
        ("Machines", reverse("kg_machine_category_list")),
        (
            six.text_type(obj.category),
            reverse("kg_machine_category_detail", args=[obj.category.pk])
        ),
        (six.text_type(obj), reverse("kg_machine_detail", args=[obj.pk]))
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def machine_add_comment(request, machine_id):
    obj = get_object_or_404(Machine, pk=machine_id)
    breadcrumbs = [
        ("Machines", reverse("kg_machine_category_list")),
        (
            six.text_type(obj.category),
            reverse("kg_machine_category_detail", args=[obj.category.pk])
        ),
        (six.text_type(obj), reverse("kg_machine_detail", args=[obj.pk]))
    ]
    return util.add_comment(request, breadcrumbs, obj)


@login_required
def category_list(request):
    queryset = MachineCategory.objects.all()

    table = MachineCategoryTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render_to_response(
        'karaage/machines/machinecategory_list.html',
        {'table': table},
        context_instance=RequestContext(request))


@admin_required
def category_create(request):
    from karaage.common.create_update import create_object
    return create_object(
        request, model=MachineCategory,
        form_class=MachineCategoryForm,
        template_name="karaage/machines/machinecategory_form.html")


@admin_required
def category_edit(request, category_id):
    from karaage.common.create_update import update_object
    return update_object(
        request, object_id=category_id, model=MachineCategory,
        form_class=MachineCategoryForm,
        template_name="karaage/machines/machinecategory_form.html")


@login_required
def category_detail(request, category_id):
    machine_category = get_object_or_404(MachineCategory, pk=category_id)

    queryset = machine_category.machine_set.all()
    table = MachineTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render_to_response(
        'karaage/machines/machinecategory_detail.html',
        {'machine_category': machine_category, 'table': table},
        context_instance=RequestContext(request))


@admin_required
def category_accounts(request, category_id):
    machine_category = get_object_or_404(MachineCategory, pk=category_id)

    queryset = machine_category.account_set.all()
    table = AccountTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render_to_response(
        'karaage/machines/machinecategory_accounts.html',
        {'machine_category': machine_category, 'table': table},
        context_instance=RequestContext(request))


@admin_required
def category_projects(request, category_id):
    machine_category = get_object_or_404(MachineCategory, pk=category_id)

    queryset = Project.objects.filter(
        projectquota__machine_category=machine_category)
    table = ProjectTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render_to_response(
        'karaage/machines/machinecategory_projects.html',
        {'machine_category': machine_category, 'table': table},
        context_instance=RequestContext(request))


@admin_required
def category_logs(request, category_id):
    obj = get_object_or_404(MachineCategory, pk=category_id)
    breadcrumbs = [
        ("Machines", reverse("kg_machine_category_list")),
        (
            six.text_type(obj),
            reverse("kg_machine_category_detail", args=[obj.pk])
        )
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def category_add_comment(request, category_id):
    obj = get_object_or_404(MachineCategory, pk=category_id)
    breadcrumbs = [
        ("Machines", reverse("kg_machine_category_list")),
        (
            six.text_type(obj),
            reverse("kg_machine_category_detail", args=[obj.pk])
        )
    ]
    return util.add_comment(request, breadcrumbs, obj)
