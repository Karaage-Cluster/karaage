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

class ProjectJoinRequest(Request):
    leader_approved = models.BooleanField()

class ProjectCreateRequest(Request):
    needs_account = models.BooleanField()

