# Copyright 2007-2014 VPAC
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

from model_utils import FieldTracker

from karaage.people.models import Person, Group
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory, Account
from karaage.projects.managers import ActiveProjectManager, DeletedProjectManager
from karaage.common import log, is_admin
from karaage.common.models import CHANGE


class Project(models.Model):
    pid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group)
    institute = models.ForeignKey(Institute)
    leaders = models.ManyToManyField(Person, related_name='leads')
    description = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    start_date = models.DateField(default=datetime.datetime.today)
    end_date = models.DateField(null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Person, related_name='project_approver', null=True, blank=True, editable=False)
    date_approved = models.DateField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey(Person, related_name='project_deletor', null=True, blank=True, editable=False)
    date_deleted = models.DateField(null=True, blank=True, editable=False)
    last_usage = models.DateField(null=True, blank=True, editable=False)
    objects = models.Manager()
    active = ActiveProjectManager()
    deleted = DeletedProjectManager()

    _tracker = FieldTracker()

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

        for field in self._tracker.changed():
            log(None, self, 2, 'Changed %s to %s' % (field,  getattr(self, field)))


        # update the datastore
        from karaage.datastores import machine_category_save_project
        machine_category_save_project(self)

        # has group changed?
        if self._tracker.has_changed("group_id"):
            old_group_pk = self._tracker.previous("group_id")
            new_group = self.group
            if old_group_pk is not None:
                old_group = Group.objects.get(pk=group_pk)
                from karaage.datastores import machine_category_remove_account_from_project
                for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                    machine_category_remove_account_from_project(account, self)
            if new_group is not None:
                from karaage.datastores import machine_category_add_account_to_project
                for account in Account.objects.filter(person__groups=new_group, date_deleted__isnull=True):
                    machine_category_add_account_to_project(account, self)
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # ensure nothing connects to this project
        query = Account.objects.filter(default_project=self)
        query.update(default_project=None)

        # delete the object
        super(Project, self).delete(*args, **kwargs)

        # update datastore associations
        old_group_pk = self._tracker.previous("group_id")
        if old_group_pk is not None:
            old_group = Group.objects.get(pk=group_pk)
            from karaage.datastores import machine_category_remove_account_from_project
            for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                machine_category_remove_account_from_project(account, self)

        # update the datastore
        from karaage.datastores import machine_category_delete_project
        machine_category_delete_project(self)
    delete.alters_data = True

    # Can user view this self record?
    def can_view(self, request):
        person = request.user

        if not person.is_authenticated():
            return False

        if is_admin(request):
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

    @property
    def machine_categories(self):
        for pq in self.projectquota_set.all():
            yield pq.machine_category


class ProjectQuota(models.Model):
    project = models.ForeignKey(Project)
    cap = models.IntegerField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)

    _tracker = FieldTracker()

    def save(self, *args, **kwargs):
        super(ProjectQuota, self).save(*args, **kwargs)

        for field in self._tracker.changed():
            log(None, self.project, 2, 'Quota %s: Changed %s to %s' %
                    (self.machine_category, field,  getattr(self, field)))
        from karaage.datastores import machine_category_save_project
        machine_category_save_project(self.project)

    def delete(self, *args, **kwargs):
        super(InstituteQuota, self).delete(*args, **kwargs)
        from karaage.datastores import machine_category_delete_project
        machine_category_delete_project(self.project, self.machine_category)

    class Meta:
        db_table = 'project_quota'
        unique_together = ('project', 'machine_category')

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


def _leaders_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    #print "'%s','%s','%s','%s','%s'"%(instance, action, reverse, model, pk_set)

    if action == "post_add":
        if not reverse:
            project = instance
            for person in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Added person to project %s leaders" % project)
                log(None, project, CHANGE, "Added person %s to project leaders" % person)
        else:
            person = instance
            for project in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Added person to project %s leaders" % project)
                log(None, project, CHANGE, "Added person %s to project leaders" % person)

    elif action == "post_remove":
        if not reverse:
            project = instance
            for person in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Removed person from project %s leaders" % project)
                log(None, project, CHANGE, "Removed person %s from project leaders" % person)
        else:
            person = instance
            for project in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Removed person from project %s leaders" % project)
                log(None, project, CHANGE, "Removed person %s from project leaders" % person)

    elif action == "pre_clear":
        # This has to occur in pre_clear, not post_clear, as otherwise
        # we won't see what project leaders need to be removed.
        if not reverse:
            project = instance
            log(None, project, CHANGE, "Removed all project leaders")
            for person in project.leaders.all():
                log(None, project, CHANGE, "Removed person %s from project leaders" % person)
        else:
            person = instance
            log(None, person, CHANGE, "Removed person from all project leaders")
            for project in person.leads.all():
                log(None, project, CHANGE, "Removed person %s from project leaders" % person)

models.signals.m2m_changed.connect(_leaders_changed, sender=Project.leaders.through)
