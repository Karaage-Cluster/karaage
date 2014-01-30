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

import datetime
import warnings

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from jsonfield import JSONField

from karaage.people.models import Person, Group
from karaage.machines.managers import MachineCategoryManager, MachineManager, ActiveMachineManager
from karaage.common import log, new_random_token

class MachineCategory(models.Model):
    DATASTORES = [ (i,i) for i in settings.DATASTORES.keys() ]
    name = models.CharField(max_length=100, unique=True)
    datastore = models.CharField(max_length=255, choices=DATASTORES, help_text="Modifying this value on existing categories will affect accounts created under the old datastore")
    objects = MachineCategoryManager()

    def __init__(self, *args, **kwargs):
        super(MachineCategory, self).__init__(*args, **kwargs)
        self._datastore = None
        if self.datastore:
            self._datastore = self.datastore

    class Meta:
        verbose_name_plural = 'machine categories'
        db_table = 'machine_category'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kg_machine_category_detail', [self.pk])

    def save(self, *args, **kwargs):
        # save the object
        super(MachineCategory, self).save(*args, **kwargs)

        # check if datastore changed
        moved = False
        old_datastore = self._datastore
        new_datastore = self.datastore
        if old_datastore != new_datastore:
            from karaage.datastores import set_mc_datastore
            set_mc_datastore(self, old_datastore, new_datastore)

        # log message
        log(None, self, 2, 'Saved machine category')

        self._datastore = self.datastore
    save.alters_data = True

    def delete(self):
        # delete the object
        super(Account, self).delete()
        from karaage.datastores import set_mc_datastore
        old_datastore = self._datastore
        set_mc_datastore(self, old_datastore, None)
    delete.alters_data = True


class Machine(AbstractBaseUser):
    name = models.CharField(max_length=50, unique=True)
    no_cpus = models.IntegerField()
    no_nodes = models.IntegerField()
    type = models.CharField(max_length=100)
    category = models.ForeignKey(MachineCategory)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pbs_server_host = models.CharField(max_length=50, null=True, blank=True)
    mem_per_core = models.IntegerField(help_text="In GB", null=True, blank=True)
    objects = MachineManager()
    active = ActiveMachineManager()
    scaling_factor = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        # save the object
        super(Machine, self).save(*args, **kwargs)

        # log message
        log(None, self, 2, 'Saved machine')
        log(None, self.category, 2, 'Saved machine %s' % self)

    def delete(self, *args, **kwargs):
        # save the object
        super(Machine, self).delete(*args, **kwargs)

        # log message
        log(None, self.category, 2, 'Deleted machine %s' % self)

    class Meta:
        db_table = 'machine'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kg_machine_detail', [self.id])


class Account(models.Model):
    person = models.ForeignKey(Person)
    username = models.CharField(max_length=100)
    foreign_id = models.CharField(max_length=255, null=True, blank=True,
                                  help_text='The foreign identifier from the datastore.')
    machine_category = models.ForeignKey(MachineCategory)
    default_project = models.ForeignKey('projects.Project', null=True, blank=True)
    date_created = models.DateField()
    date_deleted = models.DateField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True, help_text="In GB")
    shell = models.CharField(max_length=50)
    login_enabled = models.BooleanField(default=True)
    extra_data = JSONField(default={},
                           help_text='Datastore specific values should be stored in this field.')

    class Meta:
        unique_together = (('foreign_id', 'machine_category'))

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self._username = self.username
        self._machine_category = self.machine_category
        self._date_deleted = self.date_deleted
        self._login_enabled = self.login_enabled
        self._password = None

    class Meta:
        ordering = ['person', ]
        db_table = 'account'

    def __unicode__(self):
        return '%s on %s' % (self.username, self.machine_category.name)

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
        log(None, machine_category, 1,
            'Created account')
        return ua

    def project_list(self):
        return self.person.projects.filter(projectquota__machine_category=self.machine_category)

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
            from karaage.datastores import delete_account
            self.machine_category = old_machine_category
            delete_account(self)
            log(None, self.machine_category, 2,
                'Removed account %s from machine_category' % self)

            self.machine_category = new_machine_category
            moved = True
            log(None, self.machine_category, 2,
                'Added account %s to machine_category' % self)
            log(None, self.person, 2,
                'Changed machine_category of %s' % self)

        # check if it was renamed
        old_username = self._username
        new_username = self.username
        if old_username != new_username:
            if self.date_deleted is None and not moved:
                from karaage.datastores import set_account_username
                set_account_username(self, old_username, new_username)
            log(None, self.machine_category, 2,
                'Changed username of account %s from %s to %s' %
                (self, old_username, new_username))
            log(None, self.person, 2,
                'Changed username of %s from %s to %s' %
                (self, old_username, new_username))

        # check if deleted status changed
        old_date_deleted = self._date_deleted
        new_date_deleted = self.date_deleted
        if old_date_deleted != new_date_deleted:
            if new_date_deleted is not None:
                # account is deactivated
                from karaage.datastores import delete_account
                delete_account(self)
                log(None, self.machine_category, 3,
                    'Deactivated account of %s' % self)
                log(None, self.person, 3,
                    'Deactivated account of %s' % self)
                # deleted
            else:
                # account is reactivated
                log(None, self.machine_category, 3,
                    'Reactivated account of %s' % self)
                log(None, self.person, 3,
                    'Reactivated account of %s' % self)

        # has locked status changed?
        old_login_enabled = self._login_enabled
        new_login_enabled = self.login_enabled
        if old_login_enabled != new_login_enabled:
            if self.login_enabled:
                log(None, self.machine_category, 2,
                    'Unlocked account %s' % self)
                log(None, self.person, 2,
                    'Unlocked account %s' % self)
            else:
                log(None, self.machine_category, 2,
                    'Locked account %s' % self)
                log(None, self.person, 2,
                    'Locked account %s' % self)

        # makes sense to lock non-existant account
        if new_date_deleted is not None:
            self.login_enabled = False

        # update the datastore
        if self.date_deleted is None:
            from karaage.datastores import save_account
            save_account(self)

            if self._password is not None:
                from karaage.datastores import set_account_password
                set_account_password(self, self._password)
                log(None, self.machine_category, 2,
                    'Changed Password of %s' % self)
                log(None, self.person, 2,
                    'Changed Password of %s' % self)
                self._password = None

        # log message
        log(None, self.machine_category, 2,
            'Saved account %s' % self)
        log(None, self.person, 2,
            'Saved account %s' % self)

        # save current state
        self._username = self.username
        self._machine_category = self.machine_category
        self._date_deleted = self.date_deleted
        self._login_enabled = self.login_enabled
    save.alters_data = True

    def delete(self):
        # delete the object
        super(Account, self).delete()
        if self.date_deleted is None:
            # delete the datastore
            from karaage.datastores import delete_account
            delete_account(self)
            log(None, self.machine_category, 2,
                'Deleted account %s' % self)
    delete.alters_data = True

    def deactivate(self):
        if self.date_deleted is not None:
            raise RuntimeError("Account is deactivated")
        # save the object
        self.date_deleted = datetime.datetime.now()
        self.login_enabled = False
        self.save()
        # self.save() will delete the datastore for us.
    deactivate.alters_data = True

    def change_shell(self, shell):
        self.shell = shell
        self.save()
        # self.save() will update the datastore for us.
        log(None, self.person, 2,
            'Changed shell of %s' % self)
    change_shell.alters_data = True

    def set_password(self, password):
        if self.date_deleted is not None:
            raise RuntimeError("Account is deactivated")
        self._password = password
    set_password.alters_data = True

    def get_disk_quota(self):
        if self.disk_quota:
            return self.disk_quota

        iq = self.person.institute.institutequota_set.get(machine_category=self.machine_category)
        return iq.disk_quota

    def loginShell(self):
        return self.shell

    def lock(self):
        if self.date_deleted is not None:
            raise RuntimeError("Account is deactivated")
        self.login_enabled = False
        self.save()
    lock.alters_data = True

    def unlock(self):
        if self.date_deleted is not None:
            raise RuntimeError("Account is deactivated")
        self.login_enabled = True
        self.save()
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
