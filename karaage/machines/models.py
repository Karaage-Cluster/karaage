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
from karaage.machines.managers import MachineCategoryManager, ActiveMachineManager, MC_CACHE
from karaage.util import log_object as log


class MachineCategory(models.Model):
    OPENLDAP = 'karaage.datastores.openldap_datastore'
    DS_LDAP = 'karaage.datastores.ldap_datastore'
    AD = 'karaage.datastores.ad_datastore'
    FILES = 'karaage.datastores.files'
    DUMMY = 'karaage.datastores.dummy'
    ACCOUNT_DATASTORES = (
        (OPENLDAP, 'OpenLDAP'),
        (DS_LDAP, 'Netsacape LDAP'),
        (AD, 'Active Directory'),
        (FILES, 'Files'),
        (DUMMY, 'Dummy'),
        )
    name = models.CharField(max_length=100)
    datastore = models.CharField(max_length=255, choices=ACCOUNT_DATASTORES, default=OPENLDAP, help_text="Modifying this value on existing categories will affect accounts created under the old datastore")
    objects = MachineCategoryManager()

    class Meta:
        verbose_name_plural = 'machine categories'
        db_table = 'machine_category'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(MachineCategory, self).save(*args, **kwargs)
        # Cached information will likely be incorrect now.
        if self.id in MC_CACHE:
            del MC_CACHE[self.id]

    def delete(self):
        pk = self.pk
        super(MachineCategory, self).delete()
        try:
            del MC_CACHE[pk]
        except KeyError:
            pass
    
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

    def get_usage(self, start=datetime.date.today() - datetime.timedelta(days=90), end=datetime.date.today()):
        from karaage.util.usage import get_machine_usage
        return get_machine_usage(self, start, end)


class UserAccount(models.Model):
    user = models.ForeignKey(Person)
    username = models.CharField(max_length=100)
    machine_category = models.ForeignKey(MachineCategory)
    default_project = models.ForeignKey('projects.Project', null=True, blank=True)
    date_created = models.DateField()
    date_deleted = models.DateField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True, help_text="In GB")
    shell = models.CharField(max_length=50)

    class Meta:
        ordering = ['user', ]
        db_table = 'user_account'

    def __unicode__(self):
        return '%s %s' % (self.user.get_full_name(), self.machine_category.name)
    
    def get_absolute_url(self):
        return self.user.get_absolute_url()
    
    @classmethod
    def create(cls, person, default_project, machine_category):
        """Creates a UserAccount (if needed) and activates user.

        Keyword arguments:
        person_id -- Person id
        project_id -- Project id
        """
        ua = UserAccount.objects.create(
            user=person, username=person.username,
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
        return self.user.projects.filter(machine_categories=self.machine_category)
    
    def get_latest_usage(self):
        try:
            return self.cpujob_set.all()[:5]
        except:
            return None

    def save(self, *args, **kwargs):
        # update the datastore
        if self.date_deleted is None:
            from karaage.datastores import save_account
            save_account(self)

        # save the object
        super(UserAccount, self).save(*args, **kwargs)

        # log message
        log(None, self.user, 2,
            'Saved account on %s' % self.machine_category)

    def delete(self):
        if self.date_deleted is None:
            # update the datastore
            from karaage.datastores import delete_account
            delete_account(self)

            # delete the object
            super(UserAccount, self).delete(*args, **kwargs)

            log(None, self.user, 3,
                'Deleted account on %s' % self.machine_category)
        else:
            raise RuntimeError("Account is deactivated")

    def deactivate(self):
        if self.date_deleted is None:
            self.date_deleted = datetime.datetime.now()
            self.save()

            from karaage.datastores import delete_account
            delete_account(self)

            log(None, self.user, 3,
                'Deactivated account on %s' % self.machine_category)
        else:
            raise RuntimeError("Account is deactivated")

    def change_shell(self, shell):
        if self.date_deleted is None:
            from karaage.datastores import change_account_shell
            change_account_shell(self, shell)
        self.shell = shell
        self.save()

    def change_username(self, new_username):
        if self.username != new_username:
            from karaage.datastores import change_account_username
            if self.date_deleted is None:
                change_account_username(self, new_username)
            self.username = new_username
            self.save()
    change_username.alters_data = True

    def set_password(self, password):
        if self.date_deleted is not None:
            from karaage.datastores import set_account_password
            set_account_password(self, password)
        else:
            raise RuntimeError("Account is deactivated")

    def get_disk_quota(self):
        if self.disk_quota:
            return self.disk_quota

        iq = self.user.institute.institutechunk_set.get(machine_category=self.machine_category)
        return iq.disk_quota
    
    def loginShell(self):
        return self.shell

    def lock(self):
        if self.date_deleted is None:
            from karaage.datastores import lock_account
            lock_account(self)
        else:
            raise RuntimeError("Account is deactivated")

    def unlock(self):
        if self.date_deleted is None:
            from karaage.datastores import unlock_account
            unlock_account(self)
        else:
            raise RuntimeError("Account is deactivated")


def _remove_group(group, person):
    # if removing default project from person, then deactivate the account.
    for ua in person.useraccount_set.filter(date_deleted__isnull=True):
        # Does the default_project for ua belong to this group?
        count = group.project_set.filter(pk=ua.default_project.pk).count()
        # If yes, deactivate the ua
        if count > 0:
            ua.deactivate()


def _members_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    #print "'%s','%s','%s','%s','%s'"%(instance, action, reverse, model, pk_set)
    if action == "pre_remove":
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                _remove_group(group, person)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                _remove_group(group, person)

    elif action == "pre_clear":
        if not reverse:
            group = instance
            for person in group.members.all():
                _remove_group(group, person)
        else:
            person = instance
            for group in person.groups.all():
                _remove_group(group, person)


models.signals.m2m_changed.connect(_members_changed, sender=Group.members.through)
