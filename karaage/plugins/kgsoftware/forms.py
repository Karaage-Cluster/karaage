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

import six

from django import forms
from django.conf import settings

from karaage.people.models import Group
from karaage.machines.models import Machine

from .models import SoftwareCategory, Software
from .models import SoftwareVersion, SoftwareLicense


class SoftwareForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=None)
    name = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea())
    homepage = forms.URLField(required=False)
    tutorial_url = forms.URLField(required=False)
    academic_only = forms.BooleanField(required=False)
    restricted = forms.BooleanField(required=False,
                                    help_text="Will require admin approval")

    def __init__(self, *args, **kwargs):
        super(SoftwareForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = SoftwareCategory.objects.all()

    class Meta:
        model = Software
        fields = [
            'category', 'name', 'description', 'homepage', 'tutorial_url',
            'academic_only', 'restricted',
        ]


class AddPackageForm(SoftwareForm):
    group_name = forms.RegexField(
        "^%s$" % settings.GROUP_VALIDATION_RE,
        required=True,
        error_messages={'invalid': settings.GROUP_VALIDATION_ERROR_MSG})
    version = forms.CharField()
    module = forms.CharField(required=False)
    machines = forms.ModelMultipleChoiceField(queryset=None)
    license_version = forms.CharField(required=False)
    license_date = forms.DateField(required=False)
    license_text = forms.CharField(required=False, widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(AddPackageForm, self).__init__(*args, **kwargs)
        self.fields['machines'].queryset = Machine.active.all()

    def clean(self):

        data = self.cleaned_data

        if data['license_version'] \
                or data['license_date'] \
                or data['license_text']:
            raise forms.ValidationError(
                six.u('You must specify all fields in the license section'))

        return data

    def save(self, commit=True):
        assert commit is True

        data = self.cleaned_data

        software = super(AddPackageForm, self).save(commit=False)
        name = self.cleaned_data['group_name']
        software.group, _ = Group.objects.get_or_create(name=name)
        software.save()

        version = SoftwareVersion(
            software=software,
            version=data['version'],
            module=data['module'],
        )
        version.save()
        version.machines = data['machines']
        version.save()

        if data['license_text']:
            SoftwareLicense.objects.create(
                software=software,
                version=data['license_version'],
                date=data['license_date'],
                text=data['license_text'],
            )

        return software


class LicenseForm(forms.ModelForm):

    class Meta:
        model = SoftwareLicense
        fields = ['software', 'version', 'date', 'text']


class SoftwareVersionForm(forms.ModelForm):

    class Meta:
        model = SoftwareVersion
        fields = ['software', 'version', 'machines', 'module', 'last_used']


class SoftwareCategoryForm(forms.ModelForm):

    class Meta:
        model = SoftwareCategory
        fields = [
            'name',
        ]
