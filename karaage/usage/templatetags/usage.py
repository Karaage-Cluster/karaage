# Copyright 2007-2014 VPAC
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

import datetime;
from django import template

from karaage.machines.models import Machine
from karaage.usage.models import CPUJob

register = template.Library()

@register.assignment_tag()
def get_person_recent_usage(person):
    return CPUJob.objects.filter(account__person=person).select_related()[:5]

@register.assignment_tag()
def get_account_recent_usage(account):
    return CPUJob.objects.filter(account=account).select_related()[:5]

@register.assignment_tag()
def get_project_recent_usage(project):
    return CPUJob.objects.filter(project=project).select_related()[:5]

@register.assignment_tag()
def get_software_recent_usage(software):
    return CPUJob.objects.filter(software=software).select_related()[:5]

@register.assignment_tag()
def get_machinecategory_recent_usage(machinecategory):
    # we must do two separate queries here, otherwise mysql takes
    # ages and uses a lot of disk space.
    machines = Machine.objects.filter(category=machinecategory)
    return CPUJob.objects.filter(machine__in=machines).select_related()[:5]
