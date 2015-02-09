# Copyright 2011, 2013-2015 VPAC
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
from karaage.institutes.models import Institute, InstituteQuota
from karaage.institutes.models import InstituteDelegate
from karaage.projects.models import Project
import ajax_select.fields


class InstituteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InstituteForm, self).__init__(*args, **kwargs)
        if self.instance.group_id is None:
            self.fields['group_name'] = forms.RegexField(
                "^%s$" % settings.GROUP_VALIDATION_RE,
                required=True,
                error_messages={
                    'invalid': settings.GROUP_VALIDATION_ERROR_MSG})

    def clean_saml_entityid(self):
        if self.cleaned_data['saml_entityid'] == "":
            return None
        return self.cleaned_data['saml_entityid']

    class Meta:
        model = Institute
        fields = ('name', 'saml_entityid', 'is_active')

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            Project.objects.get(pid=name)
            raise forms.ValidationError(
                six.u('Institute name already in system'))
        except Project.DoesNotExist:
            return name

    def save(self, commit=True):
        institute = super(InstituteForm, self).save(commit=False)
        if institute.group_id is None:
            name = self.cleaned_data['group_name']
            institute.group, _ = Group.objects.get_or_create(name=name)
        if commit:
            institute.save()
        return institute


class InstituteQuotaForm(forms.ModelForm):

    class Meta:
        model = InstituteQuota
        fields = ('machine_category', 'quota', 'cap', 'disk_quota')


class DelegateForm(forms.ModelForm):
    person = ajax_select.fields.AutoCompleteSelectField(
        'person', required=True)

    class Meta:
        model = InstituteDelegate
        fields = ('person', 'send_email')
