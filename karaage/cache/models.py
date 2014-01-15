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
import datetime
import decimal

from django.db import models

from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Machine


class TaskMachineCategoryCache(models.Model):
    date = models.DateField(editable=False, auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    celery_task_id = models.CharField(max_length = 50, unique=True)
    ready = models.BooleanField(default=False)
    class Meta:
        unique_together = ('date', 'start', 'end')


class TaskCacheForMachineCategory(models.Model):
    date = models.DateField(editable=False, auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    machine_category = models.ForeignKey(MachineCategory)
    celery_task_id = models.CharField(max_length = 50, unique=True)
    ready = models.BooleanField(default=False)
    class Meta:
        unique_together = ('date', 'start', 'end', 'machine_category')


class TaskCacheForProject(models.Model):
    date = models.DateField(editable=False, auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    project = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory)
    celery_task_id = models.CharField(max_length = 50, unique=True)
    ready = models.BooleanField(default=False)
    class Meta:
        unique_together = ('date', 'start', 'end', 'project', 'machine_category')


class UsageCache(models.Model):
    date = models.DateField(editable=False, auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    cpu_time = models.DecimalField(max_digits=30, decimal_places=2)
    no_jobs = models.IntegerField()
    class Meta:
        abstract = True


class InstituteCache(UsageCache):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    class Meta:
        unique_together = ('date', 'start', 'end', 'institute', 'machine_category')


class ProjectCache(UsageCache):
    project = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory)
    class Meta:
        unique_together = ('date', 'start', 'end', 'project', 'machine_category')


class PersonCache(UsageCache):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory)
    class Meta:
        unique_together = ('date', 'start', 'end', 'person', 'project', 'machine_category')


class MachineCategoryCache(UsageCache):
    machine_category = models.ForeignKey(MachineCategory)
    available_time = models.DecimalField(max_digits=30, decimal_places=2)
    class Meta:
        unique_together = ('date', 'start', 'end', 'machine_category')

    def get_project_mpots(self, project_quota, start, end):
        project_cache = ProjectCache.objects.get(
                project=project_quota.project,
                machine_category=self.machine_category,
                start=start,
                end=end,
                date=datetime.date.today()
        )
        usage = project_cache.cpu_time
        total_time = self.available_time
        if total_time == 0:
            return 0
        TWOPLACES = decimal.Decimal(10) ** -2
        return ((usage / total_time) * 100 * 1000).quantize(TWOPLACES)

    def is_project_over_quota(self, project_quota, start, end):
        if self.get_project_mpots(project_quota, start, end) > project_quota.get_cap():
            return True
        return False

    def get_project_cap_percent(self, project_quota, start, end):
        cap = project_quota.get_cap()
        if cap == 0:
            return 'NaN'
        else:
            return (self.get_project_mpots(project_quota, start, end) / cap) * 100


class MachineCache(UsageCache):
    machine = models.ForeignKey(Machine)
    class Meta:
        unique_together = ('date', 'start', 'end', 'machine')
