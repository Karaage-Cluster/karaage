# Copyright 2007-2014 VPAC
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

from karaage.institutes.models import Institute, InstituteQuota
from karaage.institutes.models import InstituteDelegate
from karaage.projects.models import Project
import ajax_select.fields


class InstituteForm(forms.ModelForm):
    group = ajax_select.fields.AutoCompleteSelectField('group', required=True)

    def clean_saml_entityid(self):
        if self.cleaned_data['saml_entityid'] == "":
            return None
        return self.cleaned_data['saml_entityid']

    class Meta:
        model = Institute
        fields = ('name', 'group', 'saml_entityid', 'is_active')

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            project = Project.objects.get(pid=name)
            raise forms.ValidationError(u'Institute name already in system')
        except Project.DoesNotExist:
            return name


class InstituteQuotaForm(forms.ModelForm):

    class Meta:
        model = InstituteQuota
        fields = ('machine_category', 'quota', 'cap', 'disk_quota')


class DelegateForm(forms.ModelForm):
    person = ajax_select.fields.AutoCompleteSelectField('person', required=True)

    class Meta:
        model = InstituteDelegate
        fields = ('person', 'send_email')
