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
from django.conf import settings

import datetime

from karaage.people.models import Person, Group
from karaage.machines.managers import MachineCategoryManager, ActiveMachineManager
from karaage.util import log_object as log

import warnings

class MachineCategory(models.Model):
    ACCOUNT_DATASTORES = [ (i,i) for i in settings.ACCOUNT_DATASTORES.keys() ]
    name = models.CharField(max_length=100)
    datastore = models.CharField(max_length=255, choices=ACCOUNT_DATASTORES, help_text="Modifying this value on existing categories will affect accounts created under the old datastore")
    objects = MachineCategoryManager()

    class Meta:
        verbose_name_plural = 'machine categories'
        db_table = 'machine_category'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kg_machine_list',)


class Machine(models.Model):
    name = models.CharField(max_length=50)
    no_cpus = models.IntegerField()
    no_nodes = models.IntegerField()
    type = models.CharField(max_length=100)
    category = models.ForeignKey(MachineCategory)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pbs_server_host = models.CharField(max_length=50, null=True, blank=True)
    mem_per_core = models.IntegerField(help_text="In GB", null=True, blank=True)
    objects = models.Manager()
    active = ActiveMachineManager()
    scaling_factor = models.IntegerField(default=1)

    class Meta:
        db_table = 'machine'

    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_machine_detail', [self.id])

    def get_usage(self, start, end):
        from karaage.util.usage import get_machine_usage
        return get_machine_usage(self, start, end)


class Account(models.Model):
    person = models.ForeignKey(Person)
    username = models.CharField(max_length=100)
    machine_category = models.ForeignKey(MachineCategory)
    default_project = models.ForeignKey('projects.Project', null=True, blank=True)
    date_created = models.DateField()
    date_deleted = models.DateField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True, help_text="In GB")
    shell = models.CharField(max_length=50)
    login_enabled = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self._username = self.username
        self._machine_category = self.machine_category

    class Meta:
        ordering = ['person', ]
        db_table = 'account'

    def __unicode__(self):
        return '%s %s' % (self.person.get_full_name(), self.machine_category.name)
    
    def get_absolute_url(self):
        return self.person.get_absolute_url()
    
    @classmethod
    def create(cls, person, default_project, machine_category):
        """Creates a Account (if needed) and activates person.
        """
        ua = Account.objects.create(
            person=person, username=person.username,
            shell=settings.DEFAULT_SHELL,
            machine_category=machine_category,
            default_project=default_project,
            date_created=datetime.datetime.today())

        if default_project is not None:
            person.add_group(default_project.group)

        log(None, person, 1,
            'Created account on %s' % machine_category)
        return ua

    def project_list(self):
        return self.person.projects.filter(machine_categories=self.machine_category)
    
    def get_latest_usage(self):
        try:
            return self.cpujob_set.all()[:5]
        except:
            return None

    def save(self, *args, **kwargs):
        # save the object
        super(Account, self).save(*args, **kwargs)

        # check if machine_category changed
        moved = False
        old_machine_category = self._machine_category
        new_machine_category = self.machine_category
        if old_machine_category != new_machine_category:
            # update the datastore
            from karaage.datastores import delete_account
            self.machine_category = old_machine_category
            delete_account(self)
            self.machine_category = new_machine_category
            moved = True

        # check if it was renamed
        old_username = self._username
        new_username = self.username
        if old_username != self.username:
            if self.date_deleted is None and not moved:
                from karaage.datastores import set_account_username
                set_account_username(self, old_username, new_username)
            log(None, self.person, 2,
                'Changed username on %s' % self.machine_category)

        # update the datastore
        if self.date_deleted is None:
            from karaage.datastores import save_account
            save_account(self)

        # log message
        log(None, self.person, 2,
            'Saved account on %s' % self.machine_category)

        # save current state
        self._username = self.username
        self._machine_category = self.machine_category
    save.alters_data = True

    def delete(self):
        if self.date_deleted is None:
            # delete the object
            super(Account, self).delete(*args, **kwargs)

            # update the datastore
            from karaage.datastores import delete_account
            delete_account(self)
        else:
            raise RuntimeError("Account is deactivated")
    delete.alters_data = True

    def deactivate(self):
        if self.date_deleted is None:
            # save the object
            self.date_deleted = datetime.datetime.now()
            self.login_enabled = False
            self.save()

            # update the datastore
            from karaage.datastores import delete_account
            delete_account(self)

            log(None, self.person, 3,
                'Deactivated account on %s' % self.machine_category)
        else:
            raise RuntimeError("Account is deactivated")
    deactivate.alters_data = True

    def change_shell(self, shell):
        self.shell = shell
        # we call super.save() to avoid calling datastore save needlessly
        super(Account, self).save()
        if self.date_deleted is None:
            from karaage.datastores import set_account_shell
            set_account_shell(self, shell)
        log(None, self.person, 2,
            'Changed shell on %s' % self.machine_category)
    change_shell.alters_data = True

    def set_password(self, password):
        if self.date_deleted is None:
            from karaage.datastores import set_account_password
            set_account_password(self, password)
        else:
            raise RuntimeError("Account is deactivated")
    set_password.alters_data = True

    def get_disk_quota(self):
        if self.disk_quota:
            return self.disk_quota

        iq = self.person.institute.institutechunk_set.get(machine_category=self.machine_category)
        return iq.disk_quota
    
    def loginShell(self):
        return self.shell

    def lock(self):
        self.login_enabled = False
        self.save()
        if self.date_deleted is None:
            from karaage.datastores import lock_account
            lock_account(self)
        else:
            raise RuntimeError("Account is deactivated")
    lock.alters_data = True

    def unlock(self):
        self.login_enabled = True
        self.save()
        if self.date_deleted is None:
            from karaage.datastores import unlock_account
            unlock_account(self)
        else:
            raise RuntimeError("Account is deactivated")
    unlock.alters_data = True

    def is_locked(self):
        return not self.login_enabled


def _remove_group(group, person):
    # if removing default project from person, then break link first
    for ua in person.account_set.filter(date_deleted__isnull=True, default_project__isnull=False):
        # Does the default_project for ua belong to this group?
        count = group.project_set.filter(pk=ua.default_project.pk).count()
        # If yes, deactivate the ua
        if count > 0:
            ua.default_project = None
            ua.save()


def _members_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    #print "'%s','%s','%s','%s','%s'"%(instance, action, reverse, model, pk_set)
    if action == "post_remove":
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                _remove_group(group, person)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                _remove_group(group, person)

    elif action == "pre_clear":
        # This has to occur in pre_clear, not post_clear, as otherwise
        # we won't see what groups need to be removed.
        if not reverse:
            group = instance
            for person in group.members.all():
                _remove_group(group, person)
        else:
            person = instance
            for group in person.groups.all():
                _remove_group(group, person)


models.signals.m2m_changed.connect(_members_changed, sender=Group.members.through)
