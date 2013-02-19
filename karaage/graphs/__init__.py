# Copyright 2007-2010 VPAC
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

from django.conf import settings
from karaage.machines.models import MachineCategory

module = __import__(settings.GRAPH_LIB, {}, {}, [''])

grapher = module.GraphGenerator()


def gen_project_graph(project, start, end, machine_category=None):
    if machine_category is None:
        machine_category=MachineCategory.objects.get_default()
    return grapher.gen_project_graph(project, start, end, machine_category)

def gen_institutes_pie(start, end, machine_category=None):
    if machine_category is None:
        machine_category=MachineCategory.objects.get_default()
    return grapher.gen_institutes_pie(start, end, machine_category)

def gen_quota_graph():
    return grapher.gen_quota_graph()

def gen_trend_graph(start, end, machine_category=None):
    if machine_category is None:
        machine_category=MachineCategory.objects.get_default()
    return grapher.gen_trend_graph(start, end, machine_category)

def gen_institute_bar(institute, start, end, machine_category=None):
    if machine_category is None:
        machine_category=MachineCategory.objects.get_default()
    return grapher.gen_institute_bar(institute, start, end, machine_category)

def gen_institutes_trend(start, end, machine_category=None):
    if machine_category is None:
        machine_category=MachineCategory.objects.get_default()
    return grapher.gen_institutes_trend(start, end, machine_category)
