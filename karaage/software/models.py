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

from karaage.people.models import Person
from karaage.machines.models import Machine


class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'software_category'
        ordering = ['name']
    
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('kg_software_category_list', [])


class SoftwarePackage(models.Model):
    category = models.ForeignKey(SoftwareCategory, blank=True, null=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    gid = models.IntegerField(blank=True, null=True, editable=False)
    homepage = models.URLField(blank=True, null=True)
    tutorial_url = models.URLField(blank=True, null=True)
    academic_only = models.BooleanField()
    restricted = models.BooleanField(help_text="Will require admin approval")

    class Meta:
        ordering = ['name']
        db_table = 'software_package'

    def save(self, *args, **kwargs):
        from karaage.datastores.software import create_software
        self.gid = create_software(self)
        super(SoftwarePackage, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_software_detail', [self.id])

    def get_current_license(self):
        try:
            return self.softwarelicense_set.latest()
        except:
            return None

    def group_name(self):
        from karaage.datastores.software import get_name as ds_get_name
        return ds_get_name(self)

    def get_group_members(self):
        from karaage.datastores.software import get_members
        return get_members(self)


class SoftwareVersion(models.Model):
    package = models.ForeignKey(SoftwarePackage)
    version = models.CharField(max_length=100)
    machines = models.ManyToManyField(Machine)
    module = models.CharField(max_length=100, blank=True, null=True)
    last_used = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'software_version'
        ordering = ['-version']

    def __unicode__(self):
        return '%s - %s' % (self.package.name, self.version)
    
    def get_absolute_url(self):
        return self.package.get_absolute_url()

    def machine_list(self):
        machines = ''
        if self.machines.all():
            for m in self.machines.all():
                machines += '%s, ' % m.name
        return machines

        
class SoftwareLicense(models.Model):
    package = models.ForeignKey(SoftwarePackage)
    version = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    text = models.TextField()

    class Meta:
        db_table = 'software_license'
        get_latest_by = "date"
        ordering = ['-version']

    def __unicode__(self):
        return '%s - %s' % (self.package.name, self.version)

    def get_absolute_url(self):
        return self.package.get_absolute_url()
    

class SoftwareLicenseAgreement(models.Model):
    user = models.ForeignKey(Person)
    license = models.ForeignKey(SoftwareLicense)
    date = models.DateField()

    class Meta:
        db_table = 'software_license_agreement'
        get_latest_by = 'date'


class SoftwareAccessRequest(models.Model):
    person = models.ForeignKey(Person)
    software_license = models.ForeignKey(SoftwareLicense)
    request_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'software_access_request'
        get_latest_by = 'request_date'
