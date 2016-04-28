# Copyright 2010, 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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
from django.utils.encoding import python_2_unicode_compatible

from model_utils import FieldTracker

from karaage.common import log, is_admin
from karaage.people.models import Person, Group
from karaage.machines.models import Account, MachineCategory
from karaage.institutes.managers import ActiveInstituteManager


@python_2_unicode_compatible
class Institute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    delegates = models.ManyToManyField(
        Person, related_name='delegate_for',
        blank=True, through='InstituteDelegate')
    group = models.ForeignKey(Group)
    saml_entityid = models.CharField(
        max_length=200,
        null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    active = ActiveInstituteManager()

    _tracker = FieldTracker()

    class Meta:
        ordering = ['name']
        db_table = 'institute'
        app_label = 'karaage'

    def save(self, *args, **kwargs):
        created = self.pk is None

        # save the object
        super(Institute, self).save(*args, **kwargs)

        if created:
            log.add(self, 'Created')
        for field in self._tracker.changed():
            log.change(self, 'Changed %s to %s'
                       % (field, getattr(self, field)))

        # update the datastore
        from karaage.datastores import machine_category_save_institute
        machine_category_save_institute(self)

        # has group changed?
        if self._tracker.has_changed("group_id"):
            old_group_pk = self._tracker.previous("group_id")
            new_group = self.group
            if old_group_pk is not None:
                old_group = Group.objects.get(pk=old_group_pk)
                from karaage.datastores import remove_accounts_from_institute
                query = Account.objects.filter(person__groups=old_group)
                remove_accounts_from_institute(query, self)
            if new_group is not None:
                from karaage.datastores import add_accounts_to_institute
                query = Account.objects.filter(person__groups=new_group)
                add_accounts_to_institute(query, self)
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        log.delete(self, 'Deleted')
        super(Institute, self).delete(*args, **kwargs)

        # update datastore associations
        old_group_pk = self._tracker.previous("group_id")
        if old_group_pk is not None:
            old_group = Group.objects.get(pk=old_group_pk)
            from karaage.datastores import remove_accounts_from_institute
            query = Account.objects.filter(person__groups=old_group)
            remove_accounts_from_institute(query, self)

        # update the datastore
        from karaage.datastores import machine_category_delete_institute
        machine_category_delete_institute(self)
    delete.alters_data = True

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'kg_institute_detail', [self.id]

    def can_view(self, request):
        person = request.user

        if not person.is_authenticated():
            return False

        # staff members can view everything
        if is_admin(request):
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


@python_2_unicode_compatible
class InstituteQuota(models.Model):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    quota = models.DecimalField(max_digits=5, decimal_places=2)
    cap = models.IntegerField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True)

    _tracker = FieldTracker()

    class Meta:
        db_table = 'institute_quota'
        unique_together = ('institute', 'machine_category')
        app_label = 'karaage'

    def save(self, *args, **kwargs):
        created = self.pk is None

        super(InstituteQuota, self).save(*args, **kwargs)

        if created:
            log.add(
                self.institute,
                'Quota %s: Created' % self.machine_category)
        for field in self._tracker.changed():
            log.change(
                self.institute,
                'Quota %s: Changed %s to %s' %
                (self.machine_category, field, getattr(self, field)))

        from karaage.datastores import machine_category_save_institute
        machine_category_save_institute(self.institute)

        if created:
            from karaage.datastores import add_accounts_to_institute
            query = Account.objects.filter(person__groups=self.institute.group)
            add_accounts_to_institute(query, self.institute)

    def delete(self, *args, **kwargs):
        log.delete(
            self.institute,
            'Quota %s: Deleted' % self.machine_category)

        from karaage.datastores import remove_accounts_from_institute
        query = Account.objects.filter(person__groups=self.institute.group)
        remove_accounts_from_institute(query, self.institute)

        super(InstituteQuota, self).delete(*args, **kwargs)

        from karaage.datastores import machine_category_delete_institute
        machine_category_delete_institute(
            self.institute, self.machine_category)

    def __str__(self):
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

    _tracker = FieldTracker()

    class Meta:
        db_table = 'institutedelegate'
        app_label = 'karaage'

    def save(self, *args, **kwargs):
        super(InstituteDelegate, self).save(*args, **kwargs)

        for field in self._tracker.changed():
            log.change(
                self.institute,
                'Delegate %s: Changed %s to %s' %
                (self.person, field, getattr(self, field)))

    def delete(self, *args, **kwargs):
        super(InstituteDelegate, self).delete(*args, **kwargs)

        log.delete(
            self.institute,
            'Delegate %s: Deleted' % self.person)
