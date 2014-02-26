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

import datetime
import warnings

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.urlresolvers import reverse
from django.conf import settings
from jsonfield import JSONField

from model_utils import FieldTracker

from karaage.common.models import CHANGE
from karaage.common.constants import TITLES, STATES, COUNTRIES
from karaage.people.managers import ActivePersonManager, DeletedPersonManager, LeaderManager, PersonManager

from karaage.common import log, is_admin


# Note on terminology:
#
# A inactive person is a person who has been deleted. We keep there entry
# around and don't actually delete it.
#
# A locked person is a person who has not been deleted but is not allowed
# access for some reason.

class Person(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True, help_text="Required. 16 characters or fewer. Letters, numbers and underscores only")
    email = models.EmailField(null=True, db_index=True)
    short_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=60)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    saml_id = models.CharField(max_length=200, null=True, blank=True, unique=True, editable=False)
    position = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    supervisor = models.CharField(max_length=100, null=True, blank=True)
    institute = models.ForeignKey('institutes.Institute')
    title = models.CharField(choices=TITLES, max_length=10, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    state = models.CharField(choices=STATES, max_length=4, null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey('self', related_name='user_approver', null=True, blank=True)
    deleted_by = models.ForeignKey('self', related_name='user_deletor', null=True, blank=True)
    date_approved = models.DateField(null=True, blank=True)
    date_deleted = models.DateField(null=True, blank=True)
    last_usage = models.DateField(null=True, blank=True)
    expires = models.DateField(null=True, blank=True)
    is_systemuser = models.BooleanField(default=False)
    login_enabled = models.BooleanField(default=True)
    legacy_ldap_password = models.CharField(max_length=128, null=True, blank=True)
    objects = PersonManager()
    active = ActivePersonManager()
    deleted = DeletedPersonManager()
    projectleaders = LeaderManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'short_name', 'full_name', 'institute']

    _tracker = FieldTracker()

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self._password = None

    class Meta:
        verbose_name_plural = 'people'
        ordering = ['full_name', 'short_name']
        db_table = 'person'

    def __unicode__(self):
        name = self.get_full_name()
        if not name:
            name = "No Name"
        return name

    def get_absolute_url(self):
        return reverse('kg_person_detail', kwargs={'username': self.username})

    @staticmethod
    def is_authenticated():
        """ Return yes, this person is not anonymous. """
        return True

    def save(self, *args, **kwargs):
        # save the object
        super(Person, self).save(*args, **kwargs)

        for field in self._tracker.changed():
            if field != "password":
                log(None, self, 2, 'Changed %s to %s' % (field,  getattr(self, field)))

        # update the datastore
        from karaage.datastores import global_save_person
        global_save_person(self)

        # update account datastores
        from karaage.datastores import machine_category_save_account
        for ua in self.account_set.filter(date_deleted__isnull=True):
            machine_category_save_account(ua)

        # has username changed?
        self._tracker.has_changed("username")
        if self._tracker.has_changed("username"):
            old_username = self._tracker.previous('username')
            if old_username is not None:
                from karaage.datastores import global_set_person_username
                global_set_person_username(self, old_username, self.username)
                log(None, self, 2, 'Renamed')

        # has locked status changed?
        if self._tracker.has_changed("login_enabled"):
            if self.login_enabled:
                for ua in self.account_set.filter(date_deleted__isnull=True):
                    ua.unlock()
            else:
                for ua in self.account_set.filter(date_deleted__isnull=True):
                    ua.lock()

        # has the institute changed?
        if self._tracker.has_changed("institute_id"):
            from karaage.institutes.models import Institute
            old_institute_pk = self._tracker.previous("institute_id")
            new_institute = self.institute
            if old_institute_pk is not None:
                old_institute = Institute.objects.get(pk=old_institute_pk)
                from karaage.datastores import machine_category_remove_account_from_institute
                for account in self.account_set.filter(date_deleted__isnull=True):
                    machine_category_remove_account_from_institute(account, old_institute)
            if new_institute is not None:
                from karaage.datastores import machine_category_add_account_to_institute
                for account in self.account_set.filter(date_deleted__isnull=True):
                    machine_category_add_account_to_institute(account, new_institute)

        if self._password is not None:
            from karaage.datastores import global_set_person_password
            global_set_person_password(self, self._password)
            for ua in self.account_set.filter(date_deleted__isnull=True):
                ua.set_password(self._password)
                ua.save()
            log(None, self, 2, 'Changed Password')
            self._password = None
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        super(Person, self).delete(*args, **kwargs)

        # update the datastore
        from karaage.datastores import global_delete_person
        global_delete_person(self)
    delete.alters_data = True

    @property
    def last_name(self):
        if not self.full_name:
            return None
        elif self.full_name.find(" ") != -1:
            _, _, last_name = self.full_name.rpartition(" ")
            return last_name.strip()
        else:
            return self.full_name

    @property
    def first_name(self):
        if not self.full_name:
            return None
        elif self.full_name.find(" ") != -1:
            first_name, _, _ = self.full_name.rpartition(" ")
            return first_name.strip()
        else:
            return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission? (depreciated)"
        warnings.warn('Person.has_perm obsolete (get)', DeprecationWarning)
        raise RuntimeError("Do not use")
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`? (depreciated)"
        warnings.warn('Person.has_module_perms obsolete (get)', DeprecationWarning)
        raise RuntimeError("Do not use")
        return True

    @property
    def user(self):
        "(depreciated)"
        warnings.warn('Person.user obsolete (get)', DeprecationWarning)
        raise RuntimeError("Do not use")
        return self

    def get_profile(self):
        "(depreciated)"
        warnings.warn('Person.get_profile() obsolete (get)', DeprecationWarning)
        raise RuntimeError("Do not use")
        return self

    @property
    def is_staff(self):
        "Is the user a member of staff? (depreciated)"
        warnings.warn('Person.has_module_perms obsolete (get)', DeprecationWarning)
        raise RuntimeError("Do not use")
        return self.is_admin

    # Can person view this self record?
    def can_view(self, request):
        from karaage.projects.models import Project
        person = request.user

        if not person.is_authenticated():
            return False

        # staff members can view everything
        if is_admin(request):
            return True

        # ensure person making request isn't locked.
        if not person.is_active:
            return False

        if person.is_locked():
            return False

        # we don't allow people to see inactive accounts.
        if not self.is_active:
            return False

        # person can view own self
        if self.id == person.id:
            return True

        # Institute delegate==person can view any member of institute
        if self.institute.is_active:
            if person in self.institute.delegates.all():
                return True

        # Institute delegate==person can view people in projects that are a member of institute
        if Project.objects.filter(group__members=self.id).filter(institute__delegates=person):
            return True

        # person can view people in projects they belong to
        tmp = Project.objects.filter(group__members=self.id).filter(group__members=person.id).filter(is_active=True)
        if tmp.count() > 0:
            return True

        # Leader==person can view people in projects they lead
        tmp = Project.objects.filter(group__members=self.id).filter(leaders=person.id).filter(is_active=True)
        if tmp.count() > 0:
            return True
        return False

    def get_full_name(self):
        """ Get the full name of the person. """
        return self.full_name

    def get_short_name(self):
        """ Get the abbreviated name of the person. """
        return self.short_name

    def has_account(self, machine_category):
        ua = self.account_set.all()
        ua = ua.filter(machine_category=machine_category, date_deleted__isnull=True)
        if ua.count() != 0:
            return True
        return False

    def get_account(self, machine_category):
        try:
            return self.account_set.get(machine_category=machine_category, date_deleted__isnull=True)
        except:
            return None

    def is_leader(self):
        if self.leads.count() > 0:
            return True
        return False

    def activate(self, approved_by):
        if not self.is_active:
            self.date_approved = datetime.datetime.today()

            self.approved_by = approved_by
            self.deleted_by = None
            self.date_deleted = None
            self.is_active = True
            self.save()

            log(None, self, 2, 'Activated by %s'%approved_by)
    activate.alters_data = True

    def deactivate(self, deleted_by):
        """ Sets Person not active and deletes all Accounts"""
        self.is_active = False
        self.expires = None

        self.date_deleted = datetime.datetime.today()
        self.deleted_by = deleted_by
        self.groups.clear()
        self.save()

        for ua in self.account_set.filter(date_deleted__isnull=True):
            ua.deactivate()

        log(None, self, 2, 'Deactivated by %s'%deleted_by)
    deactivate.alters_data = True

    def set_password(self, password):
        super(Person, self).set_password(password)
        if self.legacy_ldap_password is not None:
            self.legacy_ldap_password = None
        self._password = password
    set_password.alters_data = True

    def lock(self):
        if self.is_locked():
            return
        self.login_enabled = False
        self.save()
    lock.alters_data = True

    def unlock(self):
        if not self.is_locked():
            return
        self.login_enabled = True
        self.save()
    unlock.alters_data = True

    def is_locked(self):
        return not self.login_enabled

    def add_group(self, group):
        group.members.add(self)
    add_group.alters_data = True

    def remove_group(self, group):
        group.members.remove(self)
    remove_group.alters_data = True

    @property
    def projects(self):
        from karaage.projects.models import Project
        return Project.objects.filter(group__members=self)

    @property
    def institutes(self):
        from karaage.institutes.models import Institute
        return Institute.objects.filter(group__members=self)

    @property
    def software(self):
        from karaage.software.models import Software
        return Software.objects.filter(group__members=self)


class Group(models.Model):
    """Groups represent collections of people, these objects can be
    expressed externally in a datastore."""
    name = models.CharField(max_length=100, unique=True)
    foreign_id = models.CharField(max_length=255, null=True, unique=True,
                                  help_text='The foreign identifier from the datastore.')
    members = models.ManyToManyField(Person, related_name='groups')
    description = models.TextField(null=True, blank=True)
    extra_data = JSONField(default={},
                           help_text='Datastore specific values should be stored in this field.')

    _tracker = FieldTracker()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"%s" % self.name

    def get_absolute_url(self):
        return reverse('kg_group_detail', kwargs={'group_name': self.name})

    def save(self, *args, **kwargs):
        # save the object
        super(Group, self).save(*args, **kwargs)

        for field in self._tracker.changed():
            log(None, self, 2, 'Changed %s to %s' % (field,  getattr(self, field)))

        old_name = self._tracker.previous("name")
        new_name = self.name
        if old_name is not None and old_name != new_name:
            from karaage.datastores import global_set_group_name
            global_set_group_name(self, old_name, new_name)
            from karaage.datastores import machine_category_set_group_name
            machine_category_set_group_name(self, old_name, new_name)
            log(None, self, 2, "Renamed group")

        # update the datastore
        from karaage.datastores import global_save_group
        global_save_group(self)
        from karaage.datastores import machine_category_save_group
        machine_category_save_group(self)

    save.alters_data = True

    def delete(self, *args, **kwargs):
        for person in self.members.all():
            _remove_person_from_group(person, self)

        # delete the object
        super(Group, self).delete(*args, **kwargs)

        # update the datastore
        from karaage.datastores import global_delete_group
        global_delete_group(self)
        from karaage.datastores import machine_category_delete_group
        machine_category_delete_group(self)
    delete.alters_data = True

    def add_person(self, person):
        self.members.add(person)
    add_person.alters_data = True

    def remove_person(self, person):
        self.members.remove(person)
    remove_person.alters_data = True


def _add_person_to_group(person, group):
    """ Call datastores after adding a person to a group. """
    from karaage.datastores import global_add_person_to_group
    from karaage.datastores import machine_category_add_account_to_group
    from karaage.datastores import machine_category_add_account_to_project
    from karaage.datastores import machine_category_add_account_to_institute
    from karaage.datastores import machine_category_add_account_to_software

    a_list = list(person.account_set.filter(date_deleted__isnull=True))
    global_add_person_to_group(person, group)
    for account in a_list:
        machine_category_add_account_to_group(account, group)
    for project in group.project_set.all():
        for account in a_list:
            machine_category_add_account_to_project(account, project)
    for institute in group.institute_set.all():
        for account in a_list:
            machine_category_add_account_to_institute(account, institute)
    for software in group.software_set.all():
        for account in a_list:
            machine_category_add_account_to_software(account, software)

def _remove_person_from_group(person, group):
    """ Call datastores after removing a person from a group. """
    from karaage.datastores import global_remove_person_from_group
    from karaage.datastores import machine_category_remove_account_from_group
    from karaage.datastores import machine_category_remove_account_from_project
    from karaage.datastores import machine_category_remove_account_from_institute
    from karaage.datastores import machine_category_remove_account_from_software

    a_list = list(person.account_set.filter(date_deleted__isnull=True))
    global_remove_person_from_group(person, group)
    for account in a_list:
        machine_category_remove_account_from_group(account, group)
    for project in group.project_set.all():
        for account in a_list:
            machine_category_remove_account_from_project(account, project)
    for institute in group.institute_set.all():
        for account in a_list:
            machine_category_remove_account_from_institute(account, institute)
    for software in group.software_set.all():
        for account in a_list:
            machine_category_remove_account_from_software(account, software)

def _members_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    #print "'%s','%s','%s','%s','%s'"%(instance, action, reverse, model, pk_set)

    if action == "post_add":
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Added person to group %s" % group)
                log(None, group, CHANGE, "Added person %s to group" % person)
                _add_person_to_group(person, group)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Added person to group %s" % group)
                log(None, group, CHANGE, "Added person %s to group" % person)
                _add_person_to_group(person, group)

    elif action == "post_remove":
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Removed person from group %s" % group)
                log(None, group, CHANGE, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                log(None, person, CHANGE, "Removed person from group %s" % group)
                log(None, group, CHANGE, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)

    elif action == "pre_clear":
        # This has to occur in pre_clear, not post_clear, as otherwise
        # we won't see what groups need to be removed.
        if not reverse:
            group = instance
            log(None, group, CHANGE, "Removed all people from group")
            for person in group.members.all():
                log(None, group, CHANGE, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)
        else:
            person = instance
            log(None, person, CHANGE, "Removed person from all groups")
            for group in person.groups.all():
                log(None, group, CHANGE, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)

models.signals.m2m_changed.connect(_members_changed, sender=Group.members.through)
