# Copyright 2015 VPAC
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

from karaage.people.models import Person, Group
from karaage.machines.models import Machine
from karaage.common import log


@python_2_unicode_compatible
class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'software_category'
        ordering = ['name']

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'kg_software_category_list', []


@python_2_unicode_compatible
class Software(models.Model):
    category = models.ForeignKey(SoftwareCategory, blank=True, null=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.SET_NULL)
    homepage = models.URLField(blank=True, null=True)
    tutorial_url = models.URLField(blank=True, null=True)
    academic_only = models.BooleanField(default=False)
    restricted = models.BooleanField(
        help_text="Will require admin approval", default=False)

    _tracker = FieldTracker()

    class Meta:
        ordering = ['name']
        db_table = 'software'

    def save(self, *args, **kwargs):
        created = self.pk is None

        # save the object
        super(Software, self).save(*args, **kwargs)

        if created:
            log.add(self, 'Created')
        for field in self._tracker.changed():
            log.change(self, 'Changed %s to %s'
                       % (field, getattr(self, field)))

    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        log.delete(self, 'Deleted')
        super(Software, self).delete(*args, **kwargs)

    delete.alters_data = True

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'kg_software_detail', [self.id]

    def get_current_license(self):
        try:
            return self.softwarelicense_set.latest()
        except:
            return None

    def group_name(self):
        return self.group.name

    def get_group_members(self):
        if self.group is None:
            return Group.objects.none()
        else:
            return self.group.members.all()


@python_2_unicode_compatible
class SoftwareVersion(models.Model):
    software = models.ForeignKey(Software)
    version = models.CharField(max_length=100)
    machines = models.ManyToManyField(Machine)
    module = models.CharField(max_length=100, blank=True, null=True)
    last_used = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'software_version'
        ordering = ['-version']

    def __str__(self):
        return '%s - %s' % (self.software.name, self.version)

    def get_absolute_url(self):
        return self.software.get_absolute_url()

    def machine_list(self):
        machines = ''
        if self.machines.all():
            for m in self.machines.all():
                machines += '%s, ' % m.name
        return machines


class SoftwareLicense(models.Model):
    software = models.ForeignKey(Software)
    version = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    text = models.TextField()

    class Meta:
        db_table = 'software_license'
        get_latest_by = "date"
        ordering = ['-version']

    def __str__(self):
        return '%s - %s' % (self.software.name, self.version)

    @models.permalink
    def get_absolute_url(self):
        return 'kg_software_license_detail', [self.id]


class SoftwareLicenseAgreement(models.Model):
    person = models.ForeignKey(Person)
    license = models.ForeignKey(SoftwareLicense)
    date = models.DateField()

    class Meta:
        db_table = 'software_license_agreement'
        get_latest_by = 'date'
