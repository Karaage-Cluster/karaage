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
from django.conf import settings

from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Machine

import ajax_select.fields

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine


class MachineCategoryForm(forms.ModelForm):
    class Meta:
        model = MachineCategory


class AccountForm(forms.Form):
    machine_category = forms.ModelChoiceField(queryset=MachineCategory.objects.all(), initial=1)
    default_project = ajax_select.fields.AutoCompleteSelectField('project', required=True)

    def clean(self):
        data = self.cleaned_data
        if 'machine_category' not in data:
            return data
        if 'default_project' not in data:
            return data
        if not data['machine_category'] in data['default_project'].machine_categories.all():
            raise forms.ValidationError(u'Default project not in machine category')
        return data


class ShellForm(forms.Form):
    shell = forms.ChoiceField(choices=settings.SHELLS)

    def save(self, account):
        account.change_shell(self.cleaned_data['shell'])
