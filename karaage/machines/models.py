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

from andsome.middleware.threadlocals import get_current_user

from karaage.people.models import Person
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

        from karaage.datastores import create_account
        create_account(ua)

        from karaage.datastores import add_group
        for group in person.groups.all():
            add_group(ua, group)

        if default_project is not None:
            from karaage.projects.utils import add_user_to_project
            add_user_to_project(person, default_project)

        log(get_current_user(), ua.user, 1,
            'Created account on %s' % ua.machine_category)

        return ua

    def project_list(self):
        return self.user.projects.filter(machine_categories=self.machine_category)
    
    def get_latest_usage(self):
        try:
            return self.cpujob_set.all()[:5]
        except:
            return None

    def deactivate(self):
        if not self.date_deleted:
            self.date_deleted = datetime.datetime.now()
            self.save()

        from karaage.projects.utils import remove_user_from_project
        for project in self.project_list():
            remove_user_from_project(self.user, project)

        from karaage.datastores import delete_account
        delete_account(self)

        log(get_current_user(), self.user, 3,
            'Deleted account on %s' % self.machine_category)

    def change_shell(self, shell):
        from karaage.datastores import change_shell
        change_shell(self, shell)
        self.shell = shell
        self.save()

    def set_password(self, password):
        from karaage.datastores import set_account_password
        set_account_password(self, password)

    def get_disk_quota(self):
        if self.disk_quota:
            return self.disk_quota

        iq = self.user.institute.institutechunk_set.get(machine_category=self.machine_category)
        return iq.disk_quota
    
    def loginShell(self):
        return self.shell

    def lock(self):
        from karaage.datastores import lock_account
        lock_account(self)

    def unlock(self):
        from karaage.datastores import unlock_account
        unlock_account(self)
