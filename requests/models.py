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



class UserRequest(models.Model):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project, null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)
    leader_approved = models.BooleanField()
    needs_account = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['date']
        db_table = 'user_request'

    def __unicode__(self):
        return self.person.get_full_name()
    
    def get_absolute_url(self):
        return '/users/accounts/requests/%i/' % self.id



class ProjectRequest(models.Model):
    project = models.ForeignKey(Project)
    user_request = models.ForeignKey(UserRequest, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['date']
        db_table = 'project_request'

    def __unicode__(self):
        return '%s %s' % (self.project.name, self.user_request.person.get_full_name())


