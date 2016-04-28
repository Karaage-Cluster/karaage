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

import datetime
import decimal

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from karaage.machines.models import Account, Machine, MachineCategory
from karaage.projects.models import Project
from karaage.people.models import Person
from karaage.institutes.models import Institute

from karaage.plugins.kgsoftware.models import SoftwareVersion


@python_2_unicode_compatible
class Queue(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'queue'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CPUJob(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    machine = models.ForeignKey(Machine, blank=True, null=True)
    date = models.DateField(db_index=True, blank=True, null=True)
    queue = models.ForeignKey(Queue, blank=True, null=True)
    cpu_usage = models.BigIntegerField(blank=True, null=True)
    mem = models.BigIntegerField(blank=True, null=True)
    vmem = models.BigIntegerField(blank=True, null=True)
    ctime = models.DateTimeField(blank=True, null=True)
    qtime = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    act_wall_time = models.BigIntegerField(blank=True, null=True)
    est_wall_time = models.BigIntegerField(blank=True, null=True)
    jobid = models.CharField(max_length=50, blank=True, null=True, unique=True)
    cores = models.BigIntegerField(blank=True, null=True)
    list_mem = models.BigIntegerField(blank=True, null=True)
    list_pmem = models.BigIntegerField(blank=True, null=True)
    list_vmem = models.BigIntegerField(blank=True, null=True)
    list_pvmem = models.BigIntegerField(blank=True, null=True)
    exit_status = models.BigIntegerField(blank=True, null=True)
    jobname = models.CharField(max_length=256, blank=True, null=True)
    software = models.ManyToManyField(SoftwareVersion, blank=True)

    class Meta:
        ordering = ['-date']
        db_table = 'cpu_job'

    def __str__(self):
        if self.jobid:
            return self.jobid
        return ('%s - %s - %s - %s'
                % (self.username, self.project, self.machine, self.date))

    @models.permalink
    def get_absolute_url(self):
        return 'kg_usage_job_detail', [self.jobid]

    def wait_time(self):
        diff = self.start - self.qtime
        d = (diff.days * 86400) + diff.seconds
        return d


class UsedModules(models.Model):
    jobid = models.CharField(max_length=100, primary_key=True)
    date_added = models.DateField(auto_now_add=True)
    modules = models.TextField()

    class Meta:
        db_table = 'usage_usedmodules'


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
        unique_together = (
            'date', 'start', 'end', 'institute', 'machine_category')
        db_table = 'cache_institutecache'


class ProjectCache(UsageCache):
    project = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory)

    class Meta:
        unique_together = (
            'date', 'start', 'end', 'project', 'machine_category')
        db_table = 'cache_projectcache'


class PersonCache(UsageCache):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory)

    class Meta:
        unique_together = (
            'date', 'start', 'end', 'person', 'project', 'machine_category')
        db_table = 'cache_personcache'


class MachineCategoryCache(UsageCache):
    machine_category = models.ForeignKey(MachineCategory)
    available_time = models.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        unique_together = ('date', 'start', 'end', 'machine_category')
        db_table = 'cache_machinecategorycache'

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
        two_places = decimal.Decimal(10) ** -2
        return ((usage / total_time) * 100 * 1000).quantize(two_places)

    def is_project_over_quota(self, project_quota, start, end):
        mpots = self.get_project_mpots(project_quota, start, end)
        cap = project_quota.get_cap()
        return bool(mpots > cap)

    def get_project_cap_percent(self, project_quota, start, end):
        mpots = self.get_project_mpots(project_quota, start, end)
        cap = project_quota.get_cap()
        if cap == 0:
            return 'NaN'
        else:
            return (mpots / cap) * 100


class MachineCache(UsageCache):
    machine = models.ForeignKey(Machine)

    class Meta:
        unique_together = ('date', 'start', 'end', 'machine')
        db_table = 'cache_machinecache'
