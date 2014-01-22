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

from django.db import models
from karaage.common import log
from karaage.people.models import Person, Group
from karaage.machines.models import Account, MachineCategory
from karaage.institutes.managers import ActiveInstituteManager


class Institute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    delegates = models.ManyToManyField(Person, related_name='delegate', blank=True, null=True, through='InstituteDelegate')
    group = models.ForeignKey(Group)
    saml_entityid = models.CharField(max_length=200, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    active = ActiveInstituteManager()

    def __init__(self, *args, **kwargs):
        super(Institute, self).__init__(*args, **kwargs)
        if self.group_id is None:
            self._group = None
        else:
            self._group = self.group

    class Meta:
        ordering = ['name']
        db_table = 'institute'

    def save(self, *args, **kwargs):
        # set group if not already set
        if self.group_id is None:
            name = str(self.name.lower().replace(' ', ''))
            self.group,_ = Group.objects.get_or_create(name=name)

        # save the object
        super(Institute, self).save(*args, **kwargs)

        # update the datastore
        from karaage.datastores import save_institute
        save_institute(self)

        # has group changed?
        old_group = self._group
        new_group = self.group
        if old_group != new_group:
            if old_group is not None:
                from karaage.datastores import remove_person_from_institute
                for person in Person.objects.filter(groups=old_group):
                    remove_person_from_institute(person, self)
                from karaage.datastores import remove_account_from_institute
                for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                    remove_account_from_institute(account, self)
            if new_group is not None:
                from karaage.datastores import add_person_to_institute
                for person in Person.objects.filter(groups=new_group):
                    add_person_to_institute(person, self)
                from karaage.datastores import add_account_to_institute
                for account in Account.objects.filter(person__groups=new_group, date_deleted__isnull=True):
                    add_account_to_institute(account, self)

        # log message
        log(None, self, 2, 'Saved institute')

        # save the current state
        self._group = self.group
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        super(Institute, self).delete(*args, **kwargs)

        # update datastore associations
        old_group = self._group
        if old_group is not None:
            from karaage.datastores import remove_person_from_institute
            for person in Person.objects.filter(groups=old_group):
                remove_person_from_institute(person, self)
            from karaage.datastores import remove_account_from_institute
            for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                remove_account_from_institute(account, self)

        # update the datastore
        from karaage.datastores import delete_institute
        delete_institute(self)
    delete.alters_data = True

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kg_institute_detail', [self.id])

    def can_view(self, user):
        if not user.is_authenticated():
            return False

        person = user

        # staff members can view everything
        if person.is_admin:
            return True

        if not self.is_active:
            return False

        if not person.is_active:
            return False

        if person.is_locked():
            return False

        # Institute delegates==person can view institute
        if person in self.delegates.all():
            return True

        return False

    @property
    def machine_categories(self):
        for iq in self.institutequota_set.all():
            yield iq.machine_category


class InstituteQuota(models.Model):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    quota = models.DecimalField(max_digits=5, decimal_places=2)
    cap = models.IntegerField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'institute_quota'
        unique_together = ('institute', 'machine_category')

    def __unicode__(self):
        return '%s - %s' % (self.institute, self.machine_category)

    def get_absolute_url(self):
        return self.institute.get_absolute_url()

    def get_cap(self):
        if self.cap:
            return self.cap
        if self.quota:
            return self.quota * 1000
        return None


class InstituteDelegate(models.Model):
    person = models.ForeignKey(Person)
    institute = models.ForeignKey(Institute)
    send_email = models.BooleanField()

    class Meta:
        db_table = 'institutedelegate'
