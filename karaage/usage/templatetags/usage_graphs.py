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

from django.template import Library

from andsome.graphs.googlechart import GraphGenerator

grapher = GraphGenerator()
register = Library()


@register.simple_tag
def mc_pie_chart(machine_category, start, end):

    data = {}
    for m in machine_category.machine_set.all():
        usage = m.get_usage(start, end)
        if usage[0] is not None:
            data[m.name] = float(usage[0])
            
    return grapher.pie_chart(data_dict=data).get_url()
