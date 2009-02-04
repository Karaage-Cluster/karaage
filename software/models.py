from django.db import models
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

import datetime
#from placard.connection import LDAPConnection

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
        #conn = LDAPConnection()
        try:
            ldap_group = conn.get_group(self.gid)
            return ldap_group.name()
        except:
            return 'No LDAP Group'

    def get_group_members(self):
        #conn = LDAPConnection()
        try:
            return conn.get_group_members(self.gid)
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
