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

from karaage.people.models import Person, Group
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory
from karaage.projects.managers import ActiveProjectManager, DeletedProjectManager
from karaage.util import get_current_person


class Project(models.Model):
    pid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group)
    institute = models.ForeignKey(Institute)
    leaders = models.ManyToManyField(Person, related_name='leaders')
    description = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField()
    start_date = models.DateField(default=datetime.datetime.today)
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
        ordering = ['pid']
        db_table = 'project'

    def __unicode__(self):
        return '%s - %s' % (self.pid, self.name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_project_detail', [self.pid])
        
    def save(self, *args, **kwargs):
        # set group if not already set
        if self.group_id is None:
            name = self.pid
            self.group,_ = Group.objects.get_or_create(name=name)

        # save the object
        super(Project, self).save(*args, **kwargs)

        # update the datastore
        from karaage.datastores.projects import save_project
        save_project(self)
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        super(Project, self).delete(*args, **kwargs)

        # update the datastore
        from karaage.datastores.projects import delete_project
        delete_project(self)
    delete.alters_data = True

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
        tmp = self.group.members.filter(pk=person.pk)
        if tmp.count() > 0:
            return True

        return False

    def activate(self):
        if self.is_active == True:
            return
        self.is_active = True
        self.is_approved = True
        self.date_approved = datetime.datetime.today()
        self.approved_by = get_current_person()
        self.save()
    activate.alters_data = True

    def deactivate(self):
        self.is_active = False
        self.deleted_by = get_current_person()
        self.date_deleted = datetime.datetime.today()
        self.group.members.clear()
        self.save()
    deactivate.alters_data = True

    def get_usage(self,
                  start=datetime.date.today() - datetime.timedelta(days=90),
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
    gen_usage_graph.alters_data = True

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

