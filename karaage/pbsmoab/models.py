# Copyright 2007-2013 VPAC
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

from django.db import models

from decimal import Decimal
import datetime

from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory


class InstituteQuota(models.Model):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    quota = models.DecimalField(max_digits=5, decimal_places=2)
    cap = models.IntegerField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'institute_quota'
        unique_together = ('institute', 'machine_category')

    def __unicode__(self):
        return '%s - %s' % (self.institute, self.machine_category)

    def get_absolute_url(self):
        return self.institute.get_absolute_url()

    def get_cap(self):
        if self.cap:
            return self.cap
        if self.quota:
            return self.quota * 1000
        return None



class ProjectQuota(models.Model):
    project = models.ForeignKey(Project)
    cap = models.IntegerField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)

    class Meta:
        db_table = 'project_quota'
        unique_together = ('project', 'machine_category')

    def get_mpots(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):
        from karaage.util.helpers import get_available_time

        TWOPLACES = Decimal(10) ** -2
        usage, jobs = self.project.get_usage(start, end, self.machine_category)
        if usage is None:
            usage = Decimal('0')
        total_time, ave_cpus = get_available_time(start, end, self.machine_category)
        if total_time == 0:
            return 0
        return ((Decimal(usage) / total_time) * 100 * 1000).quantize(TWOPLACES)

    def is_over_quota(self):
        if self.get_mpots() > self.get_cap():
            return True
        return False

    def get_cap(self):
        if self.cap is not None:
            return self.cap

        try:
            iq = self.project.institute.institutequota_set.get(machine_category=self.machine_category)
        except:
            return None
        if iq.cap is not None:
            return iq.cap
        return iq.quota * 1000

    def get_cap_percent(self):
        cap = self.get_cap()
        if cap == 0:
            return 'NaN'
        else:
            return (self.get_mpots() / cap) * 100
