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

from django import forms
from placard.client import LDAPClient

from karaage.machines.models import Machine
from karaage.software.models import SoftwareCategory, SoftwarePackage, SoftwareVersion, SoftwareLicense


class SoftwarePackageForm(forms.Form):
    
    category = forms.ModelChoiceField(queryset=SoftwareCategory.objects.all())
    name = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea())
    gid = forms.ChoiceField(required=False, choices=[(x.gidNumber, x.name()) for x in LDAPClient().get_groups()])
    homepage = forms.URLField(required=False)
    tutorial_url = forms.URLField(required=False)
    academic_only = forms.BooleanField(required=False)

    def save(self, package=None):
        data = self.cleaned_data

        if package is None:
            package = SoftwarePackage()

        package.category = data['category']
        package.name = data['name']
        package.description = data['description']
        package.gid = data['gid']
        package.homepage = data['homepage']
        package.tutorial_url = data['tutorial_url']
        package.academic_only = data['academic_only']
        package.save()

        return package
        


class AddPackageForm(SoftwarePackageForm):
    
    version = forms.CharField()
    module = forms.CharField(required=False)
    machines = forms.ModelMultipleChoiceField(queryset=Machine.active.all())
    license_version = forms.CharField(required=False)
    license_date = forms.DateField(required=False)
    license_text = forms.CharField(required=False, widget=forms.Textarea())


    def clean(self):

        data = self.cleaned_data

        if data['license_version'] or data['license_date'] or  data['license_text']:
            if not 'license_version' in data or not 'license_date' in data or not 'license_text' in data:
                raise forms.ValidationError(u'You must specify all fields in the license section')

        return data


    def save(self):
        data = self.cleaned_data

        package = super(self.__class__, self).save()

        version = SoftwareVersion(
            package=package,
            version=data['version'],
            module=data['module'],
        )
        version.save()
        version.machines=data['machines']
        version.save()

        if data['license_text']:
            software_license = SoftwareLicense.objects.create(
                package=package,
                version=data['license_version'],
                date=data['license_date'],
                text=data['license_text'],
            )

        return package

        
    
