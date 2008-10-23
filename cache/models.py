from django.db import models

import datetime

from karaage.people.models import Institute, Person
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory


class UsageCache(models.Model):
    date = models.DateField(editable=False)
    start = models.DateField()
    end = models.DateField()
    cpu_hours = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    no_jobs = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class InstituteCache(UsageCache):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    
    def save(self, force_insert=False, force_update=False):
        if not self.id:
            self.date = datetime.date.today()
        super(self.__class__, self).save(force_insert, force_update)


class ProjectCache(UsageCache):
    pid = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory) 

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            self.date = datetime.date.today()
        super(self.__class__, self).save(force_insert, force_update)


class UserCache(UsageCache):
    user = models.ForeignKey(Person)
    project = models.ForeignKey(Project)

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            self.date = datetime.date.today()
        super(self.__class__, self).save(force_insert, force_update)
