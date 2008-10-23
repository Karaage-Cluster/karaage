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
    user = models.ForeignKey(UserAccount)
    username = models.CharField(max_length=50, blank=True, null=True) 
    project = models.ForeignKey(Project)
    machine = models.ForeignKey(Machine)
    date = models.DateField()
    queue = models.ForeignKey(Queue)
    cpu_usage = models.IntegerField()
    mem = models.IntegerField()
    vmem = models.IntegerField()
    ctime = models.DateTimeField()
    qtime = models.DateTimeField()
    etime = models.DateTimeField()
    start = models.DateTimeField()
    act_wall_time = models.IntegerField()
    est_wall_time = models.IntegerField()
    
    class Meta:
        ordering = ['-date']
        db_table = 'cpu_job'

    def __unicode__(self):
        return '%s - %s - %s - %s' % (self.username, self.project, self.machine, self.date)
    
    def wait_time(self):
        diff = self.start - self.qtime
        d = (diff.days * 86400) + diff.seconds
        return d
