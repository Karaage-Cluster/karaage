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

import datetime

from django import forms
from django.conf import settings

from karaage.people.utils import validate_username_for_new_account
from karaage.people.utils import UsernameException
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Machine, Account

import ajax_select.fields

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ('name', 'no_cpus', 'no_nodes', 'type', 'category',
            'start_date', 'end_date', 'pbs_server_host',
            'mem_per_core', 'scaling_factor')


class MachineCategoryForm(forms.ModelForm):
    class Meta:
        model = MachineCategory


class AdminAccountForm(forms.ModelForm):
    username = forms.CharField(label=u"Requested username", max_length=16, help_text=u"16 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    machine_category = forms.ModelChoiceField(queryset=MachineCategory.objects.all(), initial=1)
    default_project = ajax_select.fields.AutoCompleteSelectField('project', required=True)
    shell = forms.ChoiceField(choices=settings.SHELLS)

    def __init__(self, person, **kwargs):
        self.person = person
        super(AdminAccountForm, self).__init__(**kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            validate_username_for_new_account(self.person, username)
        except UsernameException, e:
            raise forms.ValidationError(e.args[0])
        return username

    def clean_default_project(self):
        data = self.cleaned_data
        if 'default_project' not in data:
            return data
        default_project = data['default_project']

        query = self.person.projects.filter(pk=default_project.pk)
        if query.count() == 0:
            raise forms.ValidationError(u'Person does not belong to default project.')

        return default_project

    def clean(self):
        data = self.cleaned_data
        if 'username' not in data:
            return data
        if 'machine_category' not in data:
            return data
        if 'default_project' not in data:
            return data
        username = data['username']
        default_project = data['default_project']
        machine_category = data['machine_category']

        query = default_project.projectquota_set.filter(machine_category=machine_category)
        if query.count() == 0:
            raise forms.ValidationError(u'Default project not in machine category.')

        query = Account.objects.filter(
                    username__exact=username, machine_category=machine_category, date_deleted__isnull=True)
        if self.instance.pk is not None:
            query = query.exclude(pk=self.instance.pk)
        if query.count() > 0:
            raise forms.ValidationError(u'Username already in use on machine category %s.' % machine_category)

        return data

    def save(self, **kwargs):
        if self.instance.pk is None:
            self.instance.person = self.person
            self.instance.date_created = datetime.date.today()
        return super(AdminAccountForm, self).save(**kwargs)

    class Meta:
        model = Account
        fields = ('username', 'machine_category', 'default_project', 'disk_quota', 'shell')


class UserAccountForm(forms.ModelForm):
    shell = forms.ChoiceField(choices=settings.SHELLS)

    class Meta:
        model = Account
        fields = ('shell',)


class AddProjectForm(forms.Form):
    project = ajax_select.fields.AutoCompleteSelectField('project', required=True, label='Add to existing project')
