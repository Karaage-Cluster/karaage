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

import django_tables2 as tables
from django_tables2.utils import A
import django_filters
from django.utils.safestring import mark_safe

from .models import Project

from karaage.people.tables import PeopleColumn


class ProjectFilter(django_filters.FilterSet):
    pid = django_filters.CharFilter(lookup_type="icontains", label="PID")
    name = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Project
        fields = ('pid', 'name', 'institute', 'is_approved', 'is_active')


class ProjectTable(tables.Table):
    is_active = tables.Column(order_by=('-is_active'), verbose_name="active")
    pid = tables.LinkColumn(
        'kg_project_detail', args=[A('pk')], verbose_name="PID")
    institute = tables.LinkColumn(
        'kg_institute_detail', args=[A('institute.pk')])
    leaders = PeopleColumn(orderable=False)

    def render_is_active(self, record):
        if not record.is_active:
            html = '<span class="no">No</span>'
        else:
            html = '<span class="yes">Yes</span>'
        return mark_safe(html)

    class Meta:
        model = Project
        fields = ('is_active', 'pid', 'name', 'institute',
                  'leaders', 'last_usage')
