from django.db import models

from datetime import datetime

from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory

class UserRequest(models.Model):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project, null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)
    leader_approved = models.BooleanField()
    needs_account = models.BooleanField()
    date = models.DateField(null=True, blank=True, default=datetime.now)

    class Meta:
        ordering = ['date']
    
    def __unicode__(self):
        return self.person.get_full_name()
    
    def get_absolute_url(self):
        return '/users/accounts/requests/%i/' % self.id



class ProjectRequest(models.Model):
    project = models.ForeignKey(Project)
    user_request = models.ForeignKey(UserRequest, null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=datetime.now)

    class Meta:
        ordering = ['date']

    def __unicode__(self):
        return '%s %s' % (self.project.name, self.user_request.person.get_full_name())


