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
from django.contrib.admin.widgets import AdminDateWidget
from django.conf import settings
import datetime

import ajax_select.fields

from karaage.people.models import Group
from karaage.institutes.models import Institute
from karaage.projects.models import Project, ProjectQuota


class ProjectForm(forms.ModelForm):
    pid = forms.RegexField(
        "^%s$" % settings.PROJECT_VALIDATION_RE,
        max_length=settings.PROJECT_ID_MAX_LENGTH,
        required=False,
        label='PID',
        help_text='Leave blank for auto generation',
        error_messages={'invalid': settings.PROJECT_VALIDATION_ERROR_MSG})
    name = forms.CharField(
        label='Project Title', widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField', 'rows': 10, 'cols': 40}),
        required=False)
    institute = forms.ModelChoiceField(queryset=Institute.active.all())
    additional_req = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField', 'rows': 10, 'cols': 40}),
        required=False)
    leaders = ajax_select.fields.AutoCompleteSelectMultipleField(
        'person', required=False)
    start_date = forms.DateField(
        widget=AdminDateWidget, initial=datetime.datetime.today)
    end_date = forms.DateField(widget=AdminDateWidget, required=False)

    class Meta:
        model = Project
        fields = (
            'pid', 'name', 'institute', 'leaders', 'description',
            'start_date', 'end_date', 'additional_req')

    def __init__(self, *args, **kwargs):
        # Make PID field read only if we are editing a project
        super(ProjectForm, self).__init__(*args, **kwargs)
        instance = self.instance
        if instance.pid:
            self.fields['pid'].widget.attrs['readonly'] = True
            self.fields['pid'].help_text = \
                "You can't change the PID of an existing project"
        if instance.group_id is None:
            self.fields['group_name'] = forms.RegexField(
                "^%s$" % settings.GROUP_VALIDATION_RE,
                required=False,
                error_messages=
                {'invalid': settings.GROUP_VALIDATION_ERROR_MSG})
            index = self.fields.keyOrder.index("pid")
            self.fields.keyOrder.remove("group_name")
            self.fields.keyOrder.insert(index+1, "group_name")

    def clean_pid(self):
        pid = self.cleaned_data['pid']
        try:
            Institute.objects.get(name=pid)
            raise forms.ValidationError(u'Project ID not available')
        except Institute.DoesNotExist:
            return pid

    def clean_group_name(self):
        pid = self.cleaned_data['pid']
        group_name = self.cleaned_data['group_name']

        if pid and not group_name:
            raise forms.ValidationError(
                u'If PID given, then group is required.')
        if not pid and group_name:
            raise forms.ValidationError(
                u'If PID not given, then group must be left empty.')
        return group_name

    def save(self, commit=True):
        project = super(ProjectForm, self).save(commit=False)
        if project.group_id is None:
            name = self.cleaned_data['project_name']
            project.group, _ = Group.objects.get_or_create(name=name)
        if commit:
            project.save()
        return project


class UserProjectForm(forms.ModelForm):
    name = forms.CharField(
        label='Project Title', widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField', 'rows': 10, 'cols': 40}))
    additional_req = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField', 'rows': 10, 'cols': 40}),
        required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', 'additional_req')


class AddPersonForm(forms.Form):
    person = ajax_select.fields.AutoCompleteSelectField(
        'person', required=True, label='Add user to project')


class ProjectQuotaForm(forms.ModelForm):

    class Meta:
        model = ProjectQuota
        fields = ('machine_category', 'cap')
