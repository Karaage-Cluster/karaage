# Copyright 2007-2013 VPAC
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
import decimal

from karaage.people.models import Person, Group
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory, Account
from karaage.projects.managers import ActiveProjectManager, DeletedProjectManager
from karaage.common import log


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
    is_active = models.BooleanField()
    approved_by = models.ForeignKey(Person, related_name='project_approver', null=True, blank=True, editable=False)
    date_approved = models.DateField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey(Person, related_name='project_deletor', null=True, blank=True, editable=False)
    date_deleted = models.DateField(null=True, blank=True, editable=False)
    last_usage = models.DateField(null=True, blank=True, editable=False)
    objects = models.Manager()
    active = ActiveProjectManager()
    deleted = DeletedProjectManager()

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        if self.group_id is None:
            self._group = None
        else:
            self._group = self.group

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
        from karaage.datastores import save_project
        save_project(self)

        # has group changed?
        old_group = self._group
        new_group = self.group
        if old_group != new_group:
            if old_group is not None:
                from karaage.datastores import remove_person_from_project
                for person in Person.objects.filter(groups=old_group):
                    remove_person_from_project(person, self)
                from karaage.datastores import remove_account_from_project
                for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                    remove_account_from_project(account, self)
            if new_group is not None:
                from karaage.datastores import add_person_to_project
                for person in Person.objects.filter(groups=new_group):
                    add_person_to_project(person, self)
                from karaage.datastores import add_account_to_project
                for account in Account.objects.filter(person__groups=new_group, date_deleted__isnull=True):
                    add_account_to_project(account, self)

        # log message
        log(None, self, 2, 'Saved project')

        # save the current state
        self._group = self.group
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # ensure nothing connects to this project
        query = Account.objects.filter(default_project=self)
        query.update(default_project=None)

        # delete the object
        super(Project, self).delete(*args, **kwargs)

        # update datastore associations
        old_group = self._group
        if old_group is not None:
            from karaage.datastores import remove_person_from_project
            for person in Person.objects.filter(groups=old_group):
                remove_person_from_project(person, self)
            from karaage.datastores import remove_account_from_project
            for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                remove_account_from_project(account, self)

        # update the datastore
        from karaage.datastores import delete_project
        delete_project(self)
    delete.alters_data = True

    # Can user view this self record?
    def can_view(self, user):
        if not user.is_authenticated():
            return False

        person = user

        if person.is_admin:
            return True

        if not self.is_active:
            return False

        if not person.is_active:
            return False

        if person.is_locked():
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

    def activate(self, approved_by):
        if self.is_active == True:
            return
        self.is_active = True
        self.is_approved = True
        self.date_approved = datetime.datetime.today()
        self.approved_by = approved_by
        self.save()
        log(None, self, 2, 'Activated by %s'%approved_by)
    activate.alters_data = True

    def deactivate(self, deleted_by):
        self.is_active = False
        self.deleted_by = deleted_by
        self.date_deleted = datetime.datetime.today()
        self.group.members.clear()
        self.save()
        log(None, self, 2, 'Deactivated by %s'%deleted_by)
    deactivate.alters_data = True

    def get_usage(self, start, end, machine_category):
        from karaage.cache.usage import get_project_usage
        return get_project_usage(self, start, end, machine_category)

    def gen_usage_graph(self, start, end, machine_category):
        from karaage.graphs import gen_project_graph
        gen_project_graph(self, start, end, machine_category)
    gen_usage_graph.alters_data = True

    def get_latest_usage(self):
        return self.cpujob_set.select_related()[:5]

    def get_cap(self, machine_category):
        pc = self.projectquota_set.get(machine_category=machine_category)
        return pc.get_cap()

    def get_cap_percent(self, machine_category):
        pc = self.projectquota_set.get(machine_category=machine_category)
        return pc.get_cap_percent(self)

    @property
    def machine_categories(self):
        for pq in self.projectquota_set.all():
            yield pq.machine_category


class ProjectQuota(models.Model):
    project = models.ForeignKey(Project)
    cap = models.IntegerField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)

    class Meta:
        db_table = 'project_quota'
        unique_together = ('project', 'machine_category')

    def get_mpots(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):
        from karaage.common.helpers import get_available_time

        TWOPLACES = decimal.Decimal(10) ** -2
        usage, jobs = self.project.get_usage(start, end, self.machine_category)
        if usage is None:
            usage = decimal.Decimal('0')
        total_time, ave_cpus = get_available_time(start, end, self.machine_category)
        if total_time == 0:
            return 0
        return ((decimal.Decimal(usage) / total_time) * 100 * 1000).quantize(TWOPLACES)

    def is_over_quota(self):
        if self.get_mpots() > self.get_cap():
            return True
        return False

    def get_cap(self):
        if self.cap is not None:
            return self.cap

        try:
            iq = self.project.institute.institutequota_set.get(machine_category=self.machine_category)
        except:
            return None
        if iq.cap is not None:
            return iq.cap
        return iq.quota * 1000

    def get_cap_percent(self):
        cap = self.get_cap()
        if cap == 0:
            return 'NaN'
        else:
            return (self.get_mpots() / cap) * 100
