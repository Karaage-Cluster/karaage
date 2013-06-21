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

from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Machine


class UsageCache(models.Model):
    date = models.DateField(editable=False, auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    cpu_hours = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    no_jobs = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True
        

class InstituteCache(UsageCache):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    

class ProjectCache(UsageCache):
    pid = models.ForeignKey(Project)
    machine_category = models.ForeignKey(MachineCategory)


class UserCache(UsageCache):
    user = models.ForeignKey(Person)
    project = models.ForeignKey(Project)


class MachineCache(UsageCache):
    machine = models.ForeignKey(Machine)
