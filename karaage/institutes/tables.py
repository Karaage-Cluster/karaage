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

from .models import Institute
from karaage.people.tables import PeopleColumn


class InstituteFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Institute
        fields = ('name', 'is_active')


class InstituteTable(tables.Table):
    is_active = tables.Column(order_by=('-is_active'), verbose_name="active")
    name = tables.LinkColumn('kg_institute_detail', args=[A('pk')])
    delegates = PeopleColumn(orderable=False)

    def render_is_active(self, record):
        if not record.is_active:
            html = '<span class="no">No</span>'
        else:
            html = '<span class="yes">Yes</span>'
        return mark_safe(html)

    class Meta:
        model = Institute
        fields = ('is_active', 'name')
