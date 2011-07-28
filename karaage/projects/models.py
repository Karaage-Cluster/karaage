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
from django.db.models.signals import post_save, pre_delete

import datetime
from andsome.middleware.threadlocals import get_current_user

from karaage.people.models import Person, Institute
from karaage.machines.models import MachineCategory
from karaage.projects.managers import ActiveProjectManager, DeletedProjectManager


class Project(models.Model):
    pid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(Person, blank=True, null=True)
    institute = models.ForeignKey(Institute)
    leaders = models.ManyToManyField(Person, related_name='leaders')
    description = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)
    machine_categories = models.ManyToManyField(MachineCategory, null=True, blank=True, related_name='projects')
    is_active = models.BooleanField()
    approved_by = models.ForeignKey(Person, related_name='project_approver', null=True, blank=True, editable=False)
    date_approved = models.DateField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey(Person, related_name='project_deletor', null=True, blank=True, editable=False)
    date_deleted = models.DateField(null=True, blank=True, editable=False)
    last_usage = models.DateField(null=True, blank=True, editable=False)
    objects = models.Manager()
    active = ActiveProjectManager()
    deleted = DeletedProjectManager()

    class Meta:
        ordering = ['pid',]
        db_table = 'project'

    def __unicode__(self):
        return '%s - %s' % (self.pid, self.name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_project_detail', [self.pid])
        
    @models.permalink
    def get_usage_url(self):
        return ('kg_usage_project', [self.pid])

    # Can user view this self record?
    def can_view(self, user):
        if not user.is_authenticated():
            return False

        person = user.get_profile()

        if person.user.is_staff:
            return True

        if not self.is_active:
            return False

        # Institute delegate==person can view any member of institute
        if self.institute.is_active:
            if person in self.institute.delegates.all():
                return True

        # Leader==person can view projects they lead
        tmp = self.leaders.filter(pk=person.pk)
        if tmp.count() > 0:
            return True

        # person can view own projects
        tmp = self.users.filter(pk=person.pk)
        if tmp.count() > 0:
            return True

        return False

    def activate(self):
        self.is_active = True
        self.is_approved = True
        self.date_approved = datetime.datetime.today()
        try:
            self.approved_by = get_current_user().get_profile()
        except:
            pass
        self.save()

    def deactivate(self):
        self.is_active = False
        try:
            self.deleted_by = get_current_user().get_profile()
        except:
            pass
        self.date_deleted = datetime.datetime.today()
        self.users.clear()
        self.save()

    def get_usage(self, 
                  start=datetime.date.today()-datetime.timedelta(days=90), 
                  end=datetime.date.today(),
                  machine_category=None):
        if machine_category is None:
            machine_category = MachineCategory.objects.get_default()
        from karaage.util.usage import get_project_usage
        return get_project_usage(self, start, end, machine_category)

    def gen_usage_graph(self, start, end, machine_category=None):
        if machine_category is None:
            machine_category = self.machine_category
        from karaage.graphs import gen_project_graph
        gen_project_graph(self, start, end, machine_category)

    def get_latest_usage(self):
        return self.cpujob_set.select_related()[:5]

    def get_cap(self):
        pc = self.projectchunk_set.get(machine_category=self.machine_category)
        return pc.get_cap()

    def get_cap_percent(self):
        pc = self.projectchunk_set.get(machine_category=self.machine_category)
        try:
            return (pc.get_mpots() / self.get_cap()) * 100
        except:
            return 'NAN'


def update_project_datastore(sender, **kwargs):
    project = kwargs['instance']
    from karaage.datastores.projects import create_or_update_project
    create_or_update_project(project)

def delete_project_datastore(sender, **kwargs):
    project = kwargs['instance']
    from karaage.datastores.projects import delete_project
    delete_project(project)

post_save.connect(update_project_datastore, sender=Project)
pre_delete.connect(delete_project_datastore, sender=Project)
