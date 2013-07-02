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


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine


class MachineCategoryForm(forms.ModelForm):
    class Meta:
        model = MachineCategory


class UserAccountForm(forms.Form):
    machine_category = forms.ModelChoiceField(queryset=MachineCategory.objects.all(), initial=1)
    default_project = forms.ModelChoiceField(queryset=Project.active.all())

    def clean(self):
        data = self.cleaned_data
        if 'default_project' in data:
            if not data['machine_category'] in data['default_project'].machine_categories.all():
                raise forms.ValidationError(u'Default project not in machine category')
            return data


class ShellForm(forms.Form):
    shell = forms.ChoiceField(choices=settings.SHELLS)

    def save(self, user_account):
        user_account.change_account_shell(self.cleaned_data['shell'])
