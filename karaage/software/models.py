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

from placard.client import LDAPClient

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
    category = models.ForeignKey(SoftwareCategory)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    gid = models.IntegerField(blank=True, null=True)
    homepage = models.URLField(blank=True, null=True)
    tutorial_url = models.URLField(blank=True, null=True)
    academic_only = models.BooleanField()

    class Meta:
        ordering = ['name']
        db_table = 'software_package'

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
        conn = LDAPClient()
        try:
            ldap_group = conn.get_group('gidNumber=%s' % self.gid)
            return ldap_group.name()
        except:
            return 'No LDAP Group'

    def get_group_members(self):
        conn = LDAPClient()
        try:
            return conn.get_group_members('gidNumber=%s' % self.gid)
        except:
            return []

class SoftwareVersion(models.Model):
    package = models.ForeignKey(SoftwarePackage)
    version = models.CharField(max_length=100)
    machines = models.ManyToManyField(Machine)
    module = models.CharField(max_length=100, blank=True, null=True)

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
