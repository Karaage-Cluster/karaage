from django.db import models

from karaage.machines.models import UserAccount, Machine
from karaage.projects.models import Project


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
    cpu_usage = models.IntegerField(blank=True, null=True)
    mem = models.IntegerField(blank=True, null=True)
    vmem = models.IntegerField(blank=True, null=True)
    ctime = models.DateTimeField(blank=True, null=True)
    qtime = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    act_wall_time = models.IntegerField(blank=True, null=True)
    est_wall_time = models.IntegerField(blank=True, null=True)
    jobid = models.CharField(max_length=50, blank=True, null=True, unique=True)
    cores = models.IntegerField(blank=True, null=True)
    list_mem = models.IntegerField(blank=True, null=True)
    list_pmem = models.IntegerField(blank=True, null=True)
    list_vmem = models.IntegerField(blank=True, null=True)
    list_pvmem = models.IntegerField(blank=True, null=True)
    exit_status = models.IntegerField(blank=True, null=True)
    jobname = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['-date']
        db_table = 'cpu_job'

    def __unicode__(self):
        return '%s - %s - %s - %s' % (self.username, self.project, self.machine, self.date)
    
    def wait_time(self):
        diff = self.start - self.qtime
        d = (diff.days * 86400) + diff.seconds
        return d
