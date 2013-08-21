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
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

from karaage.constants import TITLES, STATES, COUNTRIES
from karaage.people.managers import ActiveUserManager, DeletedUserManager, LeaderManager, PersonManager
from karaage.people.emails import send_reset_password_email

from karaage.util import log_object as log
from karaage.util import new_random_token, get_current_person

import datetime

class Person(models.Model):
    user = models.ForeignKey(User, unique=True)
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
    active = ActiveUserManager()
    deleted = DeletedUserManager()
    projectleaders = LeaderManager()
    
    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self._login_enabled = self.login_enabled
        if self.institute_id is None:
            self._institute = None
        else:
            self._institute = self.institute

    class Meta:
        verbose_name_plural = 'people'
        ordering = ['user__first_name', 'user__last_name']
        db_table = 'person'
        permissions = (
            ("lock_person", "Can lock/unlock a person"),
            )
    
    def __unicode__(self):
        return self.user.get_full_name()
    
    def get_absolute_url(self):
        person = get_current_person()
        if person == self:
            try:
                return reverse('kg_user_profile')
            except:
                pass
        return reverse('kg_user_detail', kwargs={'username': self.user.username})

    def get_password_reset_url(self):
        from django.utils.http import int_to_base36
        from django.contrib.auth.tokens import default_token_generator
        uid = int_to_base36(self.user.pk)
        token = default_token_generator.make_token(self.user)
        return '%s/accounts/reset/%s-%s/' % (
            settings.REGISTRATION_BASE_URL, uid, token)
    get_password_reset_url.alters_data = True

    @classmethod
    def create(cls, data):
        """Creates a new user (not active)

        Keyword arguments:
        data -- a dictonary of user data
        """

        # Generate random password if not given
        if 'password1' in data:
            password = data['password1']
        else:
            password = User.objects.make_random_password()

        # Make sure username isn't taken in Datastore
        user = User.objects.create_user(data['username'], data['email'], password)

        user.is_active = False
        user.save()

        #Create Person
        person = Person.objects.create(
            user=user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            institute=data['institute'],
            position=data.get('position', ''),
            department=data.get('department', ''),
            title=data.get('title', ''),
            address=data.get('address', ''),
            country=data.get('country', ''),
            website=data.get('website', ''),
            fax=data.get('fax', ''),
            comment=data.get('comment', ''),
            telephone=data.get('telephone', ''),
            mobile=data.get('mobile', ''),
            supervisor=data.get('supervisor', ''),
            is_systemuser=data.get('is_systemuser', ''),
            saml_id=data.get('saml_id', None),
            )

        log(None, person, 1, 'Created person')
        return person

    @classmethod
    def create_from_applicant(cls, applicant):
        data = {
            'email': applicant.email,
            'username': applicant.username,
            'title': applicant.title,
            'first_name': applicant.first_name,
            'last_name': applicant.last_name,
            'institute': applicant.institute,
            'department': applicant.department,
            'position': applicant.position,
            'telephone': applicant.telephone,
            'mobile': applicant.mobile,
            'supervisor': applicant.supervisor,
            'address': applicant.address,
            'city': applicant.city,
            'postcode': applicant.postcode,
            'country': applicant.country,
            'fax': applicant.fax,
            'saml_id': applicant.saml_id,
            }
        return cls.create(data)

    def save(self, *args, **kwargs):
        # save the object
        super(Person, self).save(*args, **kwargs)

        # update the datastore
        from karaage.datastores import save_person
        save_person(self)

        # update account datastores
        from karaage.datastores import save_account
        for ua in self.account_set.filter(date_deleted__isnull=True):
            save_account(ua)

        # has locked status changed?
        old_login_enabled = self._login_enabled
        new_login_enabled = self.login_enabled
        if old_login_enabled != new_login_enabled:
            if new_login_enabled:
                for ua in self.account_set.filter(date_deleted__isnull=True):
                    ua.unlock()
                log(None, self, 2, 'Unlocked person')
            else:
                for ua in self.account_set.filter(date_deleted__isnull=True):
                    ua.lock()
                log(None, self, 2, 'Locked person')

        # has the institute changed?
        old_institute = self._institute
        new_institute = self.institute
        if old_institute != new_institute:
            if old_institute is not None:
                from karaage.datastores import remove_person_from_institute
                remove_person_from_institute(self, old_institute)
                from karaage.datastores import remove_account_from_institute
                for account in self.account_set.filter(date_deleted__isnull=True):
                    remove_account_from_institute(account, old_institute)
            if new_institute is not None:
                from karaage.datastores import add_person_to_institute
                add_person_to_institute(self, new_institute)
                from karaage.datastores import add_account_to_institute
                for account in self.account_set.filter(date_deleted__isnull=True):
                    add_account_to_institute(account, new_institute)

        # log message
        log(None, self, 2, 'Saved person')

        # save current state
        self._login_enabled = self.login_enabled
        self._institute = self.institute
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        delete_person(self)

        # update the datastore
        super(Person, self).delete(*args, **kwargs)
        from karaage.datastores import delete_user
    delete.alters_data = True

    def _set_username(self, new_username):
        old_username = self.username
        if old_username != new_username:
            self.user.username = new_username
            self.user.save()
            from karaage.datastores import set_person_username
            set_person_username(self, old_username, new_username)
    _set_username.alters_data = True

    def _get_username(self):
        return self.user.username
    username = property(_get_username, _set_username)
    
    def _set_last_name(self, value):
        self.user.last_name = value
        self.user.save()
    _set_last_name.alters_data = True

    def _get_last_name(self):
        return self.user.last_name
    last_name = property(_get_last_name, _set_last_name)
    
    def _set_first_name(self, value):
        self.user.first_name = value
        self.user.save()
    _set_first_name.alters_data = True

    def _get_first_name(self):
        return self.user.first_name
    first_name = property(_get_first_name, _set_first_name)
    
    def _set_email(self, value):
        self.user.email = value
        self.user.save()
    _set_email.alters_data = True

    def _get_email(self):
        return self.user.email
    email = property(_get_email, _set_email)
    
    def _set_is_active(self, value):
        self.user.is_active = value
        self.user.save()
    _set_is_active.alters_data = True

    def _get_is_active(self):
        return self.user.is_active
    is_active = property(_get_is_active, _set_is_active)

    # Can person view this self record?
    def can_view(self, user):
        from karaage.projects.models import Project

        if not user.is_authenticated():
            return False

        person = user.get_profile()

        # staff members can view everything
        if person.user.is_staff:
            return True

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
        return self.user.get_full_name()
    
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

    def get_usage(self, project, start, end, machine_category):
        from karaage.util.usage import get_user_usage
        return get_user_usage(self, project, start, end, machine_category)
    
    def is_leader(self):
        if self.leaders.count() > 0:
            return True
        return False

    def activate(self):
        if not self.is_active:
            self.date_approved = datetime.datetime.today()

            self.approved_by = get_current_person()
            self.deleted_by = None
            self.date_deleted = None
            self.user.is_active = True
            self.user.save()
            self.save()

            log(None, self, 2, 'Activated')
    activate.alters_data = True

    def deactivate(self):
        """ Sets Person not active and deletes all Accounts"""
        self.user.is_active = False
        self.expires = None
        self.user.save()

        self.date_deleted = datetime.datetime.today()
        self.deleted_by = get_current_person()
        self.groups.clear()
        self.save()

        for ua in self.account_set.filter(date_deleted__isnull=True):
            ua.deactivate()

        log(None, self, 2, 'Deactivated')
    deactivate.alters_data = True

    def set_password(self, password):
        self.user.set_password(password)
        self.user.save()
        if self.legacy_ldap_password is not None:
            self.legacy_ldap_password = None
            super(Person, self).save()
        from karaage.datastores import set_person_password
        set_person_password(self, password)
        for ua in self.account_set.filter(date_deleted__isnull=True):
            ua.set_password(password)
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
        from karaage.software.models import SoftwarePackage
        return SoftwarePackage.objects.filter(group__members=self)


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(Person, related_name='groups')
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"%s" % self.name

    def get_absolute_url(self):
        return reverse('kg_group_detail', kwargs={'group_name': self.name})

    def save(self, *args, **kwargs):
        # save the object
        super(Group, self).save(*args, **kwargs)

        # update the datastore
        from karaage.datastores import save_group
        save_group(self)

        # log message
        log(None, self, 2, "Saved group")
    save.alters_data = True

    def delete(self, *args, **kwargs):
        for person in self.members.all():
            _remove_person_from_group(person, self)

        # delete the object
        super(Group, self).delete(*args, **kwargs)

        # update the datastore
        from karaage.datastores import delete_group
        delete_group(self)
    delete.alters_data = True

    def add_person(self, person):
        self.members.add(person)
    add_person.alters_data = True

    def remove_person(self, person):
        self.members.remove(person)
    remove_person.alters_data = True

    def change_name(self, new_name):
        old_name = self.name
        if old_name != new_name:
            self.name = new_name
            # we call super.save() to avoid calling datastore save needlessly
            super(Group, self).save()
            from karaage.datastores import set_group_name
            set_group_name(self, old_name, new_name)
            log(None, self, 2, "Renamed group")
    change_name.alters_data = True


def _add_person_to_group(person, group):
    """ Call datastores after adding a person to a group. """
    from karaage.datastores import add_person_to_group
    from karaage.datastores import add_person_to_project
    from karaage.datastores import add_person_to_institute
    from karaage.datastores import add_person_to_software
    from karaage.datastores import add_account_to_group
    from karaage.datastores import add_account_to_project
    from karaage.datastores import add_account_to_institute
    from karaage.datastores import add_account_to_software

    a_list = list(person.account_set.filter(date_deleted__isnull=True))
    if True:
        add_person_to_group(person, group)
        for account in a_list:
            add_account_to_group(account, group)
    for project in group.project_set.all():
        add_person_to_project(person, project)
        for account in a_list:
            add_account_to_project(account, project)
    for institute in group.institute_set.all():
        add_person_to_institute(person, institute)
        for account in a_list:
            add_account_to_institute(account, institute)
    for software in group.softwarepackage_set.all():
        add_person_to_software(person, software)
        for account in a_list:
            add_account_to_software(account, software)

def _remove_person_from_group(person, group):
    """ Call datastores after removing a person from a group. """
    from karaage.datastores import remove_person_from_group
    from karaage.datastores import remove_person_from_project
    from karaage.datastores import remove_person_from_institute
    from karaage.datastores import remove_person_from_software
    from karaage.datastores import remove_account_from_group
    from karaage.datastores import remove_account_from_project
    from karaage.datastores import remove_account_from_institute
    from karaage.datastores import remove_account_from_software

    a_list = list(person.account_set.filter(date_deleted__isnull=True))
    if True:
        remove_person_from_group(person, group)
        for account in a_list:
            remove_account_from_group(account, group)
    for project in group.project_set.all():
        remove_person_from_project(person, project)
        for account in a_list:
            remove_account_from_project(account, project)
    for institute in group.institute_set.all():
        remove_person_from_institute(person, institute)
        for account in a_list:
            remove_account_from_institute(account, institute)
    for software in group.softwarepackage_set.all():
        remove_person_from_software(person, software)
        for account in a_list:
            remove_account_from_software(account, software)

def _members_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    #print "'%s','%s','%s','%s','%s'"%(instance, action, reverse, model, pk_set)

    if action == "post_add":
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                log(None, person, 2, "Added person to group %s" % group)
                log(None, group, 2, "Added person %s to group" % person)
                _add_person_to_group(person, group)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                log(None, person, 2, "Added person to group %s" % group)
                log(None, group, 2, "Added person %s to group" % person)
                _add_person_to_group(person, group)

    elif action == "post_remove":
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                log(None, person, 2, "Removed person from group %s" % group)
                log(None, group, 2, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                log(None, person, 2, "Removed person from group %s" % group)
                log(None, group, 2, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)

    elif action == "pre_clear":
        # This has to occur in pre_clear, not post_clear, as otherwise
        # we won't see what groups need to be removed.
        if not reverse:
            group = instance
            log(None, group, 2, "Removed all people from group")
            for person in group.members.all():
                log(None, group, 2, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)
        else:
            person = instance
            log(None, person, 2, "Removed person from all groups")
            for group in person.groups.all():
                log(None, group, 2, "Removed person %s from group" % person)
                _remove_person_from_group(person, group)

models.signals.m2m_changed.connect(_members_changed, sender=Group.members.through)
