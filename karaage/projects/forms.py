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
from django.contrib.admin.widgets import AdminDateWidget, FilteredSelectMultiple
import datetime

from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.machines.models import MachineCategory
from karaage.projects.models import Project


class ProjectForm(forms.ModelForm):
    pid = forms.CharField(label='PID', help_text='Leave blank for auto generation', required=False)
    name = forms.CharField(label='Project Title', widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), required=False)
    institute = forms.ModelChoiceField(queryset=Institute.active.all())
    additional_req = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), required=False)
    leaders = forms.ModelMultipleChoiceField(queryset=Person.active.select_related(), widget=FilteredSelectMultiple('Leaders', False))
    start_date = forms.DateField(widget=AdminDateWidget, initial=datetime.datetime.today)
    end_date = forms.DateField(widget=AdminDateWidget, required=False)
    machine_categories = forms.ModelMultipleChoiceField(queryset=MachineCategory.objects.all(), widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Project
        fields = ('pid', 'name', 'institute', 'leaders', 'description', 'start_date', 'end_date', 'additional_req', 'machine_categories')

    def __init__(self, *args, **kwargs):
        # Make PID field read only if we are editing a project
        super(ProjectForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pid:
            self.fields['pid'].widget.attrs['readonly'] = True
            self.fields['pid'].help_text = "You can't change the PID of an existing project"

    def clean_pid(self):
        pid = self.cleaned_data['pid']
        try:
            Institute.objects.get(name=pid)
            raise forms.ValidationError(u'Project ID not available')
        except Institute.DoesNotExist:
            return pid
 

class UserProjectForm(forms.ModelForm):
    name = forms.CharField(label='Project Title', widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}))
    additional_req = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', 'additional_req')
