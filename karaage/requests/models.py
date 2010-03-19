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

from datetime import datetime

from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory


class Request(models.Model):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True
	ordering = ('date',)

    def __unicode__(self):
	return "%s - %s" % (self.person, self.project)

class ProjectJoinRequest(Request):
    leader_approved = models.BooleanField()

class ProjectCreateRequest(Request):
    needs_account = models.BooleanField()

