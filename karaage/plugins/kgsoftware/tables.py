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
from django_tables2.utils import A
import django_filters

from .models import Software, SoftwareLicenseAgreement


class SoftwareFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_type="icontains")
    begin__last_used = django_filters.DateFilter(
        name="softwareversion__last_used",
        lookup_type="gte")
    end_last_used = django_filters.DateFilter(
        name="softwareversion__last_used",
        lookup_type="lte")

    class Meta:
        model = Software
        fields = ('name', 'description', 'group', 'category', 'academic_only',
                  'restricted',)


class SoftwareTable(tables.Table):
    name = tables.LinkColumn('kg_software_detail', args=[A('pk')])
    group = tables.LinkColumn('kg_group_detail', args=[A('group.name')])
    softwareversion__last_used = tables.Column(verbose_name="Last used")

    class Meta:
        model = Software
        fields = ('name', 'description', 'group', 'category',
                  'softwareversion__last_used')


class SoftwareLicenseAgreementTable(tables.Table):
    software = tables.LinkColumn(
        'kg_software_detail', accessor="license.software",
        args=[A('license.software.pk')])
    license = tables.LinkColumn(
        'kg_software_license_detail', args=[A('license.pk')])
    person = tables.LinkColumn(
        'kg_person_detail', args=[A('person.username')])

    class Meta:
        model = SoftwareLicenseAgreement
        fields = ("software", "license", "person", "date")
