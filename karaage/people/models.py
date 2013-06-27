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

from andsome.middleware.threadlocals import get_current_user
from karaage.constants import TITLES, STATES, COUNTRIES
from karaage.people.managers import ActiveUserManager, DeletedUserManager, LeaderManager, PersonManager
from karaage.people.emails import send_reset_password_email

from karaage.util import log_object as log
from karaage.util import new_random_token

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
    objects = PersonManager()
    active = ActiveUserManager()
    deleted = DeletedUserManager()
    projectleaders = LeaderManager()
    
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
        person = get_current_user().get_profile()
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

        try:
            current_user = get_current_user()
            if current_user.is_anonymous():
                current_user = person.user
        except:
            current_user = person.user

        log(current_user, person, 1, 'Created')
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

    def save(self, update_datastore=True, *args, **kwargs):
        update = False
        if self.id and self.is_active:
            update = True

        super(self.__class__, self).save(*args, **kwargs)

        if update and update_datastore:
            from karaage.datastores import update_account
            for ua in self.useraccount_set.filter(date_deleted__isnull=True):
                update_account(ua)

            from karaage.datastores import update_user
            update_user(self)

    def _set_username(self, value):
        self.user.username = value
        self.user.save()

    def _get_username(self):
        return self.user.username
    username = property(_get_username, _set_username)
    
    def _set_last_name(self, value):
        self.user.last_name = value
        self.user.save()

    def _get_last_name(self):
        return self.user.last_name
    last_name = property(_get_last_name, _set_last_name)
    
    def _set_first_name(self, value):
        self.user.first_name = value
        self.user.save()

    def _get_first_name(self):
        return self.user.first_name
    first_name = property(_get_first_name, _set_first_name)
    
    def _set_email(self, value):
        self.user.email = value
        self.user.save()

    def _get_email(self):
        return self.user.email
    email = property(_get_email, _set_email)
    
    def _set_is_active(self, value):
        self.user.is_active = value
        self.user.save()

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
        ua = self.useraccount_set.all()
        ua = ua.filter(machine_category=machine_category, date_deleted__isnull=True)
        if ua.count() != 0:
            return True
        return False

    def get_user_account(self, machine_category):
        try:
            return self.useraccount_set.get(machine_category=machine_category, date_deleted__isnull=True)
        except:
            return None

    def get_usage(self, project, start, end):
        from karaage.util.usage import get_user_usage
        return get_user_usage(self, project, start, end)
    
    def is_leader(self):
        if self.leaders.count() > 0:
            return True
        return False

    def activate(self):
        if not self.is_active:
            try:
                current_user = get_current_user()
                if current_user.is_anonymous():
                    current_user = self.user
            except:
                current_user = self.user

            self.date_approved = datetime.datetime.today()

            self.approved_by = current_user.get_profile()
            self.deleted_by = None
            self.date_deleted = None
            self.user.is_active = True
            self.user.save()
            self.save(update_datastore=False)

            from karaage.datastores import activate_user
            activate_user(self)

            log(current_user, self, 1, 'Activated')

    def deactivate(self):
        """ Sets Person not active and deletes all UserAccounts"""
        self.user.is_active = False
        self.expires = None
        self.user.save()

        deletor = get_current_user()

        self.date_deleted = datetime.datetime.today()
        self.deleted_by = deletor.get_profile()
        self.save(update_datastore=False)

        from karaage.datastores import delete_account

        for ua in self.useraccount_set.filter(date_deleted__isnull=True):
            ua.deactivate()

        from karaage.datastores import delete_user
        delete_user(self)

        log(deletor, self, 3, 'Deleted')

    def set_password(self, password):
        self.user.set_password(password)
        self.user.save()
        from karaage.datastores import set_password
        set_password(self, password)
        for ua in self.useraccount_set.filter(date_deleted__isnull=True):
            ua.set_password(password)

    def lock(self):
        if self.is_locked():
            return
        for ua in self.useraccount_set.filter(date_deleted__isnull=True):
            ua.lock()
        from karaage.datastores import lock_user
        lock_user(self)
        self.login_enabled = False
        self.save()

    def unlock(self):
        if not self.is_locked():
            return
        for ua in self.useraccount_set.filter(date_deleted__isnull=True):
            ua.lock()
        from karaage.datastores import unlock_user
        unlock_user(self)
        self.login_enabled = True
        self.save()

    def is_locked(self):
        return not self.login_enabled

    def add_group(self, group):
        group.members.add(self)

    def remove_group(self, group):
        group.members.remove(self)

    @property
    def projects(self):
        from karaage.projects.models import Project
        return Project.objects.filter(group__members=self)


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(Person, related_name='groups')
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    def get_absolute_url(self):
        return reverse('kg_group_detail', kwargs={'group_name': self.name})

    def save(self, *args, **kwargs):
        # update the datastore
        from karaage.datastores import save_group
        save_group(self)

        # save the object
        super(Group, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # update the datastore
        super(self.__class__, self).delete(*args, **kwargs)
        from karaage.datastores import delete_group

        # delete the object
        delete_group(self)

    def add_person(self, person):
        self.members.add(person)

    def remove_person(self, person):
        self.members.remove(person)


def _members_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Hook that executes whenever the group members are changed.
    """
    #print "'%s','%s','%s','%s','%s'"%(instance, action, reverse, model, pk_set)
    if action == "post_add":
        from karaage.datastores import add_group
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                for ua in person.useraccount_set.filter(date_deleted__isnull=True):
                    add_group(ua, group)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                for ua in person.useraccount_set.filter(date_deleted__isnull=True):
                    add_group(ua, group)

    elif action == "post_remove":
        from karaage.datastores import remove_group
        if not reverse:
            group = instance
            for person in model.objects.filter(pk__in=pk_set):
                for ua in person.useraccount_set.filter(date_deleted__isnull=True):
                    remove_group(ua, group)
        else:
            person = instance
            for group in model.objects.filter(pk__in=pk_set):
                for ua in person.useraccount_set.filter(date_deleted__isnull=True):
                    remove_group(ua, group)

    elif action == "post_clear":
        from karaage.datastores import remove_group
        if not reverse:
            group = instance
            for person in group.members.all():
                for ua in person.useraccount_set.filter(date_deleted__isnull=True):
                    remove_group(ua, group)
        else:
            person = instance
            for group in person.groups.all():
                for ua in person.useraccount_set.filter(date_deleted__isnull=True):
                    remove_group(ua, group)


models.signals.m2m_changed.connect(_members_changed, sender=Group.members.through)
