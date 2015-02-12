# Copyright 2015 VPAC
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
from django import template

from karaage.machines.models import Machine
from ..models import CPUJob
from ..tables import CPUJobTable

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_person_recent_usage(context, person):
    queryset = CPUJob.objects.filter(account__person=person).select_related()
    table = CPUJobTable(queryset, prefix="person-%d-usage-" % person.pk)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table


@register.assignment_tag(takes_context=True)
def get_account_recent_usage(context, account):
    queryset = CPUJob.objects.filter(account=account).select_related()
    table = CPUJobTable(queryset, prefix="account-%d-usage-" % account.pk)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table


@register.assignment_tag(takes_context=True)
def get_project_recent_usage(context, project):
    queryset = CPUJob.objects.filter(project=project).select_related()
    table = CPUJobTable(queryset, prefix="project-%d-usage-" % project.pk)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table


@register.assignment_tag(takes_context=True)
def get_software_recent_usage(context, software):
    queryset = CPUJob.objects.filter(software=software).select_related()
    table = CPUJobTable(queryset, prefix="software-%d-usage-" % software.pk)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table


@register.assignment_tag(takes_context=True)
def get_machine_recent_usage(context, machine):
    queryset = CPUJob.objects.filter(machine=machine).select_related()
    table = CPUJobTable(queryset, prefix="machine-%d-usage-" % machine.pk)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table


@register.assignment_tag(takes_context=True)
def get_machinecategory_recent_usage(context, machinecategory):
    # we must do two separate queries here, otherwise mysql takes
    # ages and uses a lot of disk space.
    machines = Machine.objects.filter(category=machinecategory)
    queryset = CPUJob.objects.filter(machine__in=machines).select_related()
    table = CPUJobTable(
        queryset, prefix="category-%d-usage-" % machinecategory.pk)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table
