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
from django.db.models import Q

from placard.client import LDAPClient
from andsome.middleware.threadlocals import get_current_user
from karaage.institutes.managers import PrimaryInstituteManager, ActiveInstituteManager
from karaage.constants import TITLES, STATES, COUNTRIES
from karaage.people.managers import ActiveUserManager, DeletedUserManager, LeaderManager


class Institute(models.Model):
    name = models.CharField(max_length=100)
    delegate = models.ForeignKey('Person', related_name='delegate', null=True, blank=True)
    active_delegate = models.ForeignKey('Person', related_name='active_delegate', null=True, blank=True)
    sub_delegates = models.ManyToManyField('Person', related_name='sub_delegates', blank=True, null=True)
    gid = models.IntegerField(editable=False)
    saml_entityid = models.CharField(max_length=200, null=True, blank=True, unique=True)
    is_active = models.BooleanField()
    objects = models.Manager()
    active = ActiveInstituteManager()
    primary = PrimaryInstituteManager()

    class Meta:
        ordering = ['name']
        db_table = 'institute'

    def save(self, *args, **kwargs):
        from karaage.datastores.institutes import create_institute
        self.gid = create_institute(self)
        super(Institute, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_institute_detail', [self.id])
    
    @models.permalink
    def get_usage_url(self):
        return ('kg_usage_institute', [1, self.id])
    
    def is_primary(self):
        if self.delegate:
            return True
        return False

    def get_usage(self, start, end, machine_category=None):
        from karaage.machines.models import MachineCategory
        if machine_category is None:
            machine_category = MachineCategory.objects.get_default()
        from karaage.util.usage import get_institute_usage
        return get_institute_usage(self, start, end, machine_category)

    def gen_usage_graph(self, start, end, machine_category):
        from karaage.graphs import gen_institute_bar
        gen_institute_bar(self, start, end, machine_category)

    def can_view(self, user):
        if not user.is_authenticated():
            return False

        person = user.get_profile()

        # staff members can view everything
        if person.user.is_staff:
            return True

        if not self.is_active:
            return False

        # Institute delegate==person can view institute
        if institute.delegate.id == person.id:
            return True
        if institute.active_delegate.id == person.id:
            return True

        return False



class Person(models.Model):
    user = models.ForeignKey(User, unique=True)
    saml_id = models.CharField(max_length=200, null=True, blank=True, unique=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    supervisor = models.CharField(max_length=100, null=True, blank=True)
    institute = models.ForeignKey(Institute)
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
    objects = models.Manager()
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
        return reverse('kg_user_detail', kwargs={'username': self.user.username })

    def save(self, update_datastore=True, *args, **kwargs):
        update = False
        if self.id and self.is_active:
            update = True

        super(self.__class__, self).save(*args, **kwargs)
 
        if update and update_datastore:            
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
            if self.institute.delegate is not None:
                if self.institute.delegate.id == person.id:
                    return True
            if self.institute.active_delegate is not None:
                if  self.institute.active_delegate.id == person.id:
                    return True

        # Institute delegate==person can view people in projects that are a member of institute
        tmp = Project.objects.filter(users=self.id).filter(Q(institute__delegate=person)|Q(institute__active_delegate=person)).filter(is_active=True)
        if tmp.count() > 0:
            return True

        # person can view people in projects they belong to
        tmp = Project.objects.filter(users=self.id).filter(users=person.id).filter(is_active=True)
        if tmp.count() > 0:
            return True

        # Leader==person can view people in projects they lead
        tmp = Project.objects.filter(users=self.id).filter(leaders=person.id).filter(is_active=True)
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
    
    def is_delegate(self):
        if self.delegate.count() > 0:
            return True
        return False

    def is_active_delegate(self):
        if self.active_delegate.count() > 0:
            return True
        return False

    def activate(self):
        if not self.is_active:
            from karaage.datastores import activate_user
            activate_user(self)

    def deactivate(self):
        from karaage.datastores import delete_user
        delete_user(self)

    def set_password(self, password):
        from karaage.datastores import set_password
        set_password(self, password)

    def lock(self):
        from karaage.datastores import lock_user
        lock_user(self)

    def unlock(self):
        from karaage.datastores import unlock_user
        unlock_user(self)

    def is_locked(self):
        from karaage.datastores import is_locked
        return is_locked(self)
                
    def loginShell(self):
        conn = LDAPClient()
        try:
            ldap_user = conn.get_user('uid=%s' % self.username)
        except:
            return ''
        try:
            return ldap_user.loginShell
        except:
            return ''
