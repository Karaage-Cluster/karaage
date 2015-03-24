# Copyright 2008-2011, 2013-2015 VPAC
# Copyright 2010, 2014 The University of Melbourne
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

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible

from jsonfield import JSONField

from model_utils import FieldTracker

from karaage.people.models import Person, Group
from karaage.machines.managers import MachineCategoryManager
from karaage.machines.managers import MachineManager, ActiveMachineManager
from karaage.common import log, is_admin


@python_2_unicode_compatible
class MachineCategory(models.Model):
    DATASTORES = [(i, i) for i in settings.MACHINE_CATEGORY_DATASTORES.keys()]
    name = models.CharField(max_length=100, unique=True)
    datastore = models.CharField(
        max_length=255, choices=DATASTORES,
        help_text="Modifying this value on existing categories will affect "
        "accounts created under the old datastore")
    objects = MachineCategoryManager()

    _tracker = FieldTracker()

    def __init__(self, *args, **kwargs):
        super(MachineCategory, self).__init__(*args, **kwargs)
        self._datastore = None
        if self.datastore:
            self._datastore = self.datastore

    class Meta:
        verbose_name_plural = 'machine categories'
        db_table = 'machine_category'
        app_label = 'karaage'

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'kg_machine_category_detail', [self.pk]

    def save(self, *args, **kwargs):
        created = self.pk is None

        # save the object
        super(MachineCategory, self).save(*args, **kwargs)

        if created:
            log.add(self, 'Created')
        for field in self._tracker.changed():
            log.change(
                self, 'Changed %s to %s' % (field, getattr(self, field)))

        # check if datastore changed
        if self._tracker.has_changed("datastore"):
            old_datastore = self._tracker.previous("datastore")
            from karaage.datastores import set_mc_datastore
            set_mc_datastore(self, old_datastore, self)
    save.alters_data = True

    def delete(self, **kwargs):
        # delete the object
        log.delete(self, 'Deleted')
        super(MachineCategory, self).delete(**kwargs)
        from karaage.datastores import set_mc_datastore
        old_datastore = self._datastore
        set_mc_datastore(self, old_datastore, None)
    delete.alters_data = True


@python_2_unicode_compatible
class Machine(AbstractBaseUser):
    name = models.CharField(max_length=50, unique=True)
    no_cpus = models.IntegerField()
    no_nodes = models.IntegerField()
    type = models.CharField(max_length=100)
    category = models.ForeignKey(MachineCategory)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pbs_server_host = models.CharField(max_length=50, null=True, blank=True)
    mem_per_core = models.IntegerField(
        help_text="In GB", null=True, blank=True)
    objects = MachineManager()
    active = ActiveMachineManager()
    scaling_factor = models.IntegerField(default=1)

    _tracker = FieldTracker()

    def save(self, *args, **kwargs):
        created = self.pk is None

        # save the object
        super(Machine, self).save(*args, **kwargs)

        if created:
            log.add(self, 'Created')
            log.add(self.category, 'Machine %s: Created' % self)
        for field in self._tracker.changed():
            if field == "password":
                log.change(self, 'Changed %s' % field)
                log.change(
                    self.category,
                    'Machine %s: Changed %s' % (self, field))
            else:
                log.change(
                    self,
                    'Changed %s to %s' % (field, getattr(self, field)))
                log.change(
                    self.category,
                    'Machine %s: Changed %s to %s'
                    % (self, field, getattr(self, field)))

    def delete(self, *args, **kwargs):
        # delete the object
        log.delete(self, 'Deleted')
        log.delete(self.category, 'Machine %s: Deleted' % self)
        super(Machine, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'machine'
        app_label = 'karaage'

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'kg_machine_detail', [self.id]


@python_2_unicode_compatible
class Account(models.Model):
    person = models.ForeignKey(Person)
    username = models.CharField(max_length=255)
    foreign_id = models.CharField(
        max_length=255, null=True, unique=True,
        help_text='The foreign identifier from the datastore.')
    machine_category = models.ForeignKey(MachineCategory)
    default_project = models.ForeignKey(
        'karaage.Project', null=True, blank=True)
    date_created = models.DateField()
    date_deleted = models.DateField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True, help_text="In GB")
    shell = models.CharField(max_length=50)
    login_enabled = models.BooleanField(default=True)
    extra_data = JSONField(
        default={},
        help_text='Datastore specific values should be stored in this field.')

    _tracker = FieldTracker()

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self._password = None

    class Meta:
        ordering = ['person', ]
        db_table = 'account'
        app_label = 'karaage'

    def __str__(self):
        return '%s/%s' % (self.username, self.machine_category.name)

    def get_absolute_url(self):
        return reverse('kg_account_detail', args=[self.pk])

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

        return ua

    def project_list(self):
        return self.person.projects.filter(
            projectquota__machine_category=self.machine_category)

    def save(self, *args, **kwargs):
        created = self.pk is None

        # save the object
        super(Account, self).save(*args, **kwargs)

        if created:
            log.add(
                self.person,
                'Account %s: Created on %s' % (self, self.machine_category))
            log.add(
                self.machine_category,
                'Account %s: Created on %s' % (self, self.machine_category))
        for field in self._tracker.changed():
            if field != "password":
                log.change(
                    self.person,
                    'Account %s: Changed %s to %s'
                    % (self, field, getattr(self, field)))
                log.change(
                    self.machine_category,
                    'Account %s: Changed %s to %s'
                    % (self, field, getattr(self, field)))

        # check if machine_category changed
        moved = False
        if self._tracker.has_changed('machine_category_id'):
            old_machine_category_pk = self._tracker.previous(
                'machine_category_id')
            if old_machine_category_pk is not None:
                old_machine_category = MachineCategory.objects.get(
                    pk=old_machine_category_pk)
                old_username = self._tracker.previous('username')

                new_machine_category = self.machine_category
                new_username = self.username

                # set old values so we can delete old datastore
                self.machine_category = old_machine_category
                self.username = old_username

                from karaage.datastores import machine_category_delete_account
                machine_category_delete_account(self)
                log.change(
                    self.person,
                    'Account %s: Removed account' % self)
                log.change(
                    self.machine_category,
                    'Account %s: Removed account' % self)

                # set new values again
                self.machine_category = new_machine_category
                self.username = new_username

                log.change(
                    self.person,
                    'Account %s: Added account' % self)
                log.change(
                    self.machine_category,
                    'Account %s: Added account' % self)

                moved = True

        # check if it was renamed
        if self._tracker.has_changed('username'):
            old_username = self._tracker.previous('username')
            if old_username is not None:
                new_username = self.username
                if self.date_deleted is None and not moved:
                    from karaage.datastores \
                        import machine_category_set_account_username
                    machine_category_set_account_username(
                        self, old_username, new_username)
                log.change(
                    self.person,
                    'Account %s: Changed username from %s to %s' %
                    (self, old_username, new_username))
                log.change(
                    self.machine_category,
                    'Account %s: Changed username from %s to %s' %
                    (self, old_username, new_username))

        # check if deleted status changed
        if self._tracker.has_changed('date_deleted'):
            if self.date_deleted is not None:
                # account is deactivated
                from karaage.datastores import machine_category_delete_account
                machine_category_delete_account(self)
                log.delete(
                    self.person,
                    'Account %s: Deactivated account' % self)
                log.delete(
                    self.machine_category,
                    'Account %s: Deactivated account' % self)
                # deleted
            else:
                # account is reactivated
                log.add(
                    self.person,
                    'Account %s: Activated' % self)
                log.add(
                    self.machine_category,
                    'Account %s: Activated' % self)

        # makes sense to lock non-existant account
        if self.date_deleted is not None:
            self.login_enabled = False

        # update the datastore
        if self.date_deleted is None:
            from karaage.datastores import machine_category_save_account
            machine_category_save_account(self)

            if self._password is not None:
                from karaage.datastores \
                    import machine_category_set_account_password
                machine_category_set_account_password(self, self._password)
                log.change(
                    self.person,
                    'Account %s: Changed Password' % self)
                log.change(
                    self.machine_category,
                    'Account %s: Changed Password' % self)
                self._password = None
    save.alters_data = True

    def can_view(self, request):
        # if user not authenticated, no access
        if not request.user.is_authenticated():
            return False

        # ensure person making request isn't deleted.
        if not request.user.is_active:
            return False

        # ensure person making request isn't locked.
        if request.user.is_locked():
            return False

        # if user is admin, full access
        if is_admin(request):
            return True

        # ensure this account is not locked
        if self.is_locked():
            return False

        # ensure this account is not deleted
        if self.date_deleted is not None:
            return False

        # ensure person owning account isn't locked.
        if self.person.is_locked():
            return False

        # ensure person owning account isn't deleted.
        if not self.person.is_active:
            return False

        return True

    def can_edit(self, request):
        # if we can't view this account, we can't edit it either
        if not self.can_view(request):
            return False

        if not is_admin(request):
            # if not admin, ensure we are the person being altered
            if self.person != request.user:
                return False

        return True

    def delete(self, **kwargs):
        # delete the object
        log.delete(self.person, 'Account %s: Deleted' % self)
        log.delete(self.machine_category, 'Account %s: Deleted' % self)
        super(Account, self).delete(**kwargs)
        if self.date_deleted is None:
            # delete the datastore
            from karaage.datastores import machine_category_delete_account
            machine_category_delete_account(self)
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
    change_shell.alters_data = True

    def set_password(self, password):
        if self.date_deleted is not None:
            raise RuntimeError("Account is deactivated")
        self._password = password
    set_password.alters_data = True

    def get_disk_quota(self):
        if self.disk_quota:
            return self.disk_quota

        iq = self.person.institute.institutequota_set.get(
            machine_category=self.machine_category)
        return iq.disk_quota

    def login_shell(self):
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
    for ua in person.account_set.filter(
            date_deleted__isnull=True, default_project__isnull=False):
        # Does the default_project for ua belong to this group?
        count = group.project_set.filter(pk=ua.default_project.pk).count()
        # If yes, deactivate the ua
        if count > 0:
            ua.default_project = None
            ua.save()


def _members_changed(
        sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    # print "'%s','%s','%s','%s','%s'" \
    #   % (instance, action, reverse, model, pk_set)
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


models.signals.m2m_changed.connect(
    _members_changed, sender=Group.members.through)
