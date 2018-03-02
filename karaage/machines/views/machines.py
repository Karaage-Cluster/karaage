# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import django_tables2 as tables
import six
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import karaage.common as util
from karaage.common.decorators import admin_required, login_required
from karaage.machines.forms import MachineForm
from karaage.machines.models import Machine
from karaage.machines.tables import MachineTable


@login_required
def machine_list(request):
    queryset = Machine.objects.all()
    table = MachineTable(queryset)
    tables.RequestConfig(request).configure(table)

    return render(
        template_name='karaage/machines/machine_list.html',
        context={
            'table': table,
            'title': "Machine list",
        },
        request=request)


@login_required
def machine_detail(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    return render(
        template_name='karaage/machines/machine_detail.html',
        context={'machine': machine},
        request=request)


@admin_required
def machine_create(request):
    form = MachineForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            machine = form.save()
            return HttpResponseRedirect(machine.get_absolute_url())

    return render(
        template_name='karaage/machines/machine_form.html',
        context=locals(),
        request=request)


@admin_required
def machine_edit(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)

    form = MachineForm(request.POST or None, instance=machine)
    if request.method == 'POST':
        if form.is_valid():
            machine = form.save()
            return HttpResponseRedirect(machine.get_absolute_url())

    return render(
        template_name='karaage/machines/machine_form.html',
        context=locals(),
        request=request)


@admin_required
def machine_password(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    password = None
    if request.method == 'POST':
        password = Machine.objects.make_random_password()
        machine.set_password(password)
        machine.save()
    return render(
        template_name='karaage/machines/machine_password.html',
        context={'machine': machine, 'password': password},
        request=request)


@admin_required
def machine_logs(request, machine_id):
    obj = get_object_or_404(Machine, pk=machine_id)
    breadcrumbs = [
        ("Machines", reverse("kg_machine_list")),
        (six.text_type(obj), reverse("kg_machine_detail", args=[obj.pk]))
    ]
    return util.log_list(request, breadcrumbs, obj)


@admin_required
def machine_add_comment(request, machine_id):
    obj = get_object_or_404(Machine, pk=machine_id)
    breadcrumbs = [
        ("Machines", reverse("kg_machine_list")),
        (six.text_type(obj), reverse("kg_machine_detail", args=[obj.pk]))
    ]
    return util.add_comment(request, breadcrumbs, obj)
