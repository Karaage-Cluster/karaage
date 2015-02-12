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

from django.db.models import Q

from karaage.projects.tables import ProjectColumn

from .models import CPUJob


class UnknownUsageFilter(django_filters.BooleanFilter):

    def filter(self, qs, value):
        if value is not None:
            if value:
                qs = qs.filter(
                    Q(project__isnull=True) | Q(account__isnull=True))
            else:
                qs = qs.filter(
                    Q(project__isnull=False) & Q(account__isnull=False))
        return qs


class CPUJobFilter(django_filters.FilterSet):
    person = django_filters.CharFilter(name="account__person__username")
    account = django_filters.CharFilter(name="account__pk")
    project = django_filters.CharFilter(name="project__pid")
    unknown_usage = UnknownUsageFilter()

    class Meta:
        model = CPUJob
        fields = ('person', 'machine__category', 'queue', 'account', 'project')


class CPUJobTable(tables.Table):
    jobid = tables.LinkColumn('kg_usage_job_detail', args=[A('jobid')])
    project = ProjectColumn()
    person = tables.LinkColumn(
        'kg_person_detail', accessor="account.person",
        args=[A('account.person.username')])
    machine = tables.LinkColumn('kg_machine_detail', args=[A('machine.pk')])

    class Meta:
        model = CPUJob
        fields = ('jobid', 'person', 'project', 'machine', 'date',
                  'queue', 'cpu_usage', 'cores', 'vmem',
                  'wait_time', 'est_wall_time', 'act_wall_time')
