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

from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from model_utils import FieldTracker

from karaage.common import is_admin, log
from karaage.institutes.managers import ActiveInstituteManager
from karaage.machines.models import Account
from karaage.people.models import Group, Person


@python_2_unicode_compatible
class Institute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    delegates = models.ManyToManyField(
        Person, related_name='delegate_for',
        blank=True, through='InstituteDelegate')
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
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
        from karaage.datastores import save_institute
        save_institute(self)

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
        # Get list of accounts.
        # This must happen before we call the super method,
        # as this will delete accounts that use this institute.
        old_group_pk = self._tracker.previous("group_id")
        if old_group_pk is not None:
            old_group = Group.objects.get(pk=old_group_pk)
            query = Account.objects.filter(person__groups=old_group)
            query = query.filter(date_deleted__isnull=True)
            accounts = list(query)
        else:
            accounts = []

        # delete the object
        log.delete(self, 'Deleted')
        super(Institute, self).delete(*args, **kwargs)

        # update datastore associations
        for account in accounts:
            from karaage.datastores import remove_account_from_institute
            remove_account_from_institute(account, self)

        # update the datastore
        from karaage.datastores import delete_institute
        delete_institute(self)
    delete.alters_data = True

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('kg_institute_detail', args=[self.id])

    def can_view(self, request):
        person = request.user

        if not person.is_authenticated:
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


class InstituteDelegate(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
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
