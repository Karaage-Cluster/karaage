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

from django.db import models

from karaage.machines.models import UserAccount, Machine
from karaage.projects.models import Project
from karaage.software.models import SoftwareVersion


class Queue(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=200, blank=True, null=True)
        
    class Meta:
        db_table = 'queue'
    
    def __unicode__(self):
        return self.name
    

class CPUJob(models.Model):
    user = models.ForeignKey(UserAccount, blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True) 
    project = models.ForeignKey(Project, blank=True, null=True)
    machine = models.ForeignKey(Machine, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
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
    jobname = models.CharField(max_length=100, blank=True, null=True)
    software = models.ManyToManyField(SoftwareVersion, blank=True, null=True)

    class Meta:
        ordering = ['-date']
        db_table = 'cpu_job'

    def __unicode__(self):
        if self.jobid:
            return self.jobid
        return '%s - %s - %s - %s' % (self.username, self.project, self.machine, self.date)

    @models.permalink
    def get_absolute_url(self):
        return ('kg_job_detail', [self.jobid])
    
    def wait_time(self):
        diff = self.start - self.qtime
        d = (diff.days * 86400) + diff.seconds
        return d


class UsedModules(models.Model):
    jobid = models.CharField(max_length=100, primary_key=True)
    date_added = models.DateField(auto_now_add=True)
    modules = models.TextField()
