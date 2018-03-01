# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import ajax_select.fields
import six
from django import forms
from django.conf import settings

from karaage.machines.models import Account, Machine
from karaage.people.utils import (
    UsernameException,
    check_username_for_new_account,
    validate_username_for_new_account,
)


class MachineForm(forms.ModelForm):

    class Meta:
        model = Machine
        fields = (
            'name', 'no_cpus', 'no_nodes', 'type',
            'start_date', 'end_date', 'pbs_server_host',
            'mem_per_core', 'scaling_factor')


class AdminAccountForm(forms.ModelForm):
    username = forms.CharField(
        label=six.u("Requested username"),
        max_length=settings.USERNAME_MAX_LENGTH,
        help_text=((settings.USERNAME_VALIDATION_ERROR_MSG +
                    " and has a max length of %s.")
                   % settings.USERNAME_MAX_LENGTH))
    default_project = ajax_select.fields.AutoCompleteSelectField(
        'project', required=True)
    shell = forms.ChoiceField(choices=settings.SHELLS)

    def __init__(self, person, **kwargs):
        self.person = person
        super(AdminAccountForm, self).__init__(**kwargs)
        self.old_username = self.instance.username

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            validate_username_for_new_account(self.person, username)
        except UsernameException as e:
            raise forms.ValidationError(e.args[0])
        return username

    def clean_default_project(self):
        data = self.cleaned_data
        if 'default_project' not in data:
            return data
        default_project = data['default_project']

        query = self.person.projects.filter(pk=default_project.pk)
        if query.count() == 0:
            raise forms.ValidationError(
                six.u('Person does not belong to default project.'))

        return default_project

    def clean(self):
        data = self.cleaned_data
        if 'username' not in data:
            return data
        username = data['username']

        if (self.old_username is None or
                self.old_username != username):
            try:
                check_username_for_new_account(self.person, username)
            except UsernameException as e:
                raise forms.ValidationError(e.args[0])

        return data

    def save(self, **kwargs):
        if self.instance.pk is None:
            self.instance.person = self.person
            self.instance.date_created = datetime.date.today()
        return super(AdminAccountForm, self).save(**kwargs)

    class Meta:
        model = Account
        fields = (
            'username',
            'default_project', 'disk_quota', 'shell')


class UserAccountForm(forms.ModelForm):
    shell = forms.ChoiceField(choices=settings.SHELLS)

    class Meta:
        model = Account
        fields = ('shell',)


class AddProjectForm(forms.Form):
    project = ajax_select.fields.AutoCompleteSelectField(
        'project', required=True, label='Add to existing project')
