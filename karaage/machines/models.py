# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import copy
import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from tracking_model import TrackingModelMixin

from karaage.common import is_admin, log
from karaage.machines.managers import ActiveMachineManager, MachineManager
from karaage.people.models import Group, Person


class Machine(TrackingModelMixin, AbstractBaseUser):
    name = models.CharField(max_length=50, unique=True)
    no_cpus = models.IntegerField()
    no_nodes = models.IntegerField()
    type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pbs_server_host = models.CharField(max_length=50, null=True, blank=True)
    mem_per_core = models.IntegerField(help_text="In GB", null=True, blank=True)
    objects = MachineManager()
    active = ActiveMachineManager()
    scaling_factor = models.IntegerField(default=1)

    USERNAME_FIELD = "name"

    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            changed = {field: None for field in self.tracker.tracked_fields}
        else:
            changed = copy.deepcopy(self.tracker.changed)

        # save the object
        super(Machine, self).save(*args, **kwargs)

        if created:
            log.add(self, "Created")
        for field in changed.keys():
            if field == "password":
                log.change(self, "Changed %s" % field)
            else:
                log.change(self, "Changed %s to %s" % (field, getattr(self, field)))

    def delete(self, *args, **kwargs):
        # delete the object
        log.delete(self, "Deleted")
        super(Machine, self).delete(*args, **kwargs)

    class Meta:
        db_table = "machine"
        app_label = "karaage"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("kg_machine_detail", args=[self.id])


class Account(TrackingModelMixin, models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    foreign_id = models.CharField(
        max_length=255, null=True, unique=True, help_text="The foreign identifier from the datastore."
    )
    default_project = models.ForeignKey("karaage.Project", null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateField()
    date_deleted = models.DateField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True, help_text="In GB")
    shell = models.CharField(max_length=50)
    login_enabled = models.BooleanField(default=True)
    extra_data = models.JSONField(
        default=dict, blank=True, help_text="Datastore specific values should be stored in this field."
    )

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self._password = None

    class Meta:
        ordering = [
            "person",
        ]
        db_table = "account"
        app_label = "karaage"

    def __str__(self):
        return "%s" % self.username

    def get_absolute_url(self):
        return reverse("kg_account_detail", args=[self.pk])

    @classmethod
    def create(cls, person, default_project):
        """Creates a Account (if needed) and activates person."""
        ua = Account.objects.create(
            person=person,
            username=person.username,
            shell=settings.DEFAULT_SHELL,
            default_project=default_project,
            date_created=datetime.datetime.today(),
        )

        if default_project is not None:
            person.add_group(default_project.group)

        return ua

    def project_list(self):
        return self.person.projects.all()

    def save(self, *args, **kwargs):
        created = self.pk is None
        if created:
            changed = {field: None for field in self.tracker.tracked_fields}
        else:
            changed = copy.deepcopy(self.tracker.changed)

        # save the object
        super(Account, self).save(*args, **kwargs)

        if created:
            log.add(self.person, "Account %s: Created" % self)
        for field in changed.keys():
            if field != "password":
                log.change(self.person, "Account %s: Changed %s to %s" % (self, field, getattr(self, field)))

        # check if it was renamed
        if "username" in changed:
            old_username = changed["username"]
            if old_username is not None:
                new_username = self.username
                if self.date_deleted is None:
                    from karaage.datastores import set_account_username

                    set_account_username(self, old_username, new_username)
                log.change(
                    self.person, "Account %s: Changed username from %s to %s" % (self, old_username, new_username)
                )

        # check if deleted status changed
        if "date_deleted" in changed:
            if self.date_deleted is not None:
                # account is deactivated
                from karaage.datastores import delete_account

                delete_account(self)
                log.delete(self.person, "Account %s: Deactivated account" % self)
                # deleted
            else:
                # account is reactivated
                log.add(self.person, "Account %s: Activated" % self)

        # makes sense to lock non-existant account
        if self.date_deleted is not None:
            self.login_enabled = False

        # update the datastore
        if self.date_deleted is None:
            from karaage.datastores import save_account

            save_account(self)

            if self._password is not None:
                from karaage.datastores import set_account_password

                set_account_password(self, self._password)
                log.change(self.person, "Account %s: Changed Password" % self)
                self._password = None

    save.alters_data = True

    def can_view(self, request):
        # if user not authenticated, no access
        if not request.user.is_authenticated:
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
        log.delete(self.person, "Account %s: Deleted" % self)
        super(Account, self).delete(**kwargs)
        if self.date_deleted is None:
            # delete the datastore
            from karaage.datastores import delete_account

            delete_account(self)

    delete.alters_data = True

    def deactivate(self):
        if self.date_deleted is not None:
            raise RuntimeError("Account is deactivated")
        # save the object
        self.date_deleted = timezone.now()
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
        # FIXME: should this become deprecated?
        return self.disk_quota

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
