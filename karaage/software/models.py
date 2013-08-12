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

from karaage.people.models import Person, Group
from karaage.machines.models import Machine, Account

from karaage.util import log_object as log

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
    group = models.ForeignKey(Group, blank=True, null=True)
    homepage = models.URLField(blank=True, null=True)
    tutorial_url = models.URLField(blank=True, null=True)
    academic_only = models.BooleanField()
    restricted = models.BooleanField(help_text="Will require admin approval")

    def __init__(self, *args, **kwargs):
        super(SoftwarePackage, self).__init__(*args, **kwargs)
        if self.group_id is None:
            self._group = None
        else:
            self._group = self.group

    class Meta:
        ordering = ['name']
        db_table = 'software_package'

    def save(self, *args, **kwargs):
        # set group if not already set
        if self.group_id is None:
            name = str(self.name.lower().replace(' ', ''))
            self.group,_ = Group.objects.get_or_create(name=name)

        # has group changed?
        old_group = self._group
        new_group = self.group
        if old_group != new_group:
            if old_group is not None:
                from karaage.datastores import remove_person_from_software
                for person in Person.objects.filter(groups=old_group):
                    remove_person_from_software(person, self)
                from karaage.datastores import remove_account_from_software
                for account in Account.objects.filter(person__groups=old_group, date_deleted__isnull=True):
                    remove_account_from_software(account, self)
            if new_group is not None:
                from karaage.datastores import add_person_to_software
                for person in Person.objects.filter(groups=new_group):
                    add_person_to_software(person, self)
                from karaage.datastores import add_account_to_software
                for account in Account.objects.filter(person__groups=new_group, date_deleted__isnull=True):
                    add_account_to_software(account, self)

        # save the object
        super(SoftwarePackage, self).save(*args, **kwargs)

        # update the datastore
        from karaage.datastores import save_software
        save_software(self)

        # log message
        log(None, self, 2, "Saved software package")

        # save the current state
        self._group = self.group
    save.alters_data = True

    def delete(self, *args, **kwargs):
        # delete the object
        super(SoftwarePackage, self).delete(*args, **kwargs)

        # update the datastore
        from karaage.datastores import delete_software
        delete_software(self)
    delete.alters_data = True

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
        return self.group.name

    def get_group_members(self):
        if self.group is None:
            return Group.objects.none()
        else:
            return self.group.members.all()


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
