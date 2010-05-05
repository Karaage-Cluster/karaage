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
from django.contrib.admin.widgets import AdminDateWidget

import datetime
from andsome.middleware.threadlocals import get_current_user

from karaage.people.models import Institute, Person
from karaage.machines.models import MachineCategory
from karaage.requests.models import ProjectCreateRequest
from karaage.util.helpers import get_new_pid
from karaage.util import log_object

from models import Project


class ProjectForm(forms.ModelForm):
    name = forms.CharField(label='Project Title', widget=forms.TextInput(attrs={ 'size':60 }))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    institute = forms.ModelChoiceField(queryset=Institute.valid.all())
    additional_req = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    leaders = forms.ModelMultipleChoiceField(queryset=Person.active.all())
    start_date = forms.DateField(widget=AdminDateWidget)
    end_date = forms.DateField(widget=AdminDateWidget, required=False)
    machine_categories = forms.ModelMultipleChoiceField(queryset=MachineCategory.objects.all(), widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Project
        fields = ('name', 'institute', 'leaders', 'description', 'start_date', 'end_date', 'additional_req', 'machine_categories', 'machine_category')


class UserProjectForm(forms.Form):
    """
    This form is for people who have an account and want to start a new project
    or edit it
    """
    name = forms.CharField(label='Project Title', widget=forms.TextInput(attrs={ 'size':60 }))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }))
    additional_req = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    is_expertise = forms.BooleanField(required=False, help_text=u"Is this a current VPAC funded Expertise or Education Project?")
    pid = forms.CharField(label="PIN", max_length=10, required=False, help_text="If yes, please provide Project Identification Number")
    needs_account = forms.BooleanField(required=False, label=u"Will you be working on this project yourself?")
    #machine_categories = forms.ModelMultipleChoiceField(queryset=MachineCategory.objects.all(), widget=forms.CheckboxSelectMultiple)
    institute = forms.ModelChoiceField(queryset=Institute.valid.all())

    def save(self, leader=None, p=None):
        data = self.cleaned_data

        if p is None:
            p = Project()
            p.pid = get_new_pid(data['institute'], data['is_expertise'])
            p.institute = data['institute']
            p.machine_category=MachineCategory.objects.get_default()
            p.start_date = datetime.datetime.today()
            p.is_approved, p.is_active = False, False
            p.is_expertise = data['is_expertise']
            p.name = data['name']
            p.description = data['description']
            p.additional_req = data['additional_req']
            p.is_expertise = data['is_expertise']
            p.save()
            p.machine_categories.add(MachineCategory.objects.get_default())
            p.save()
            p.leaders.add(leader)
            project_request = ProjectCreateRequest.objects.create(
                project=p,
                person=leader,
                needs_account=data['needs_account'],
            )

            log_object(get_current_user(), p, 1, 'Created')

            return project_request

        #edit
        p.name = data['name']
        p.description = data['description']
        p.additional_req = data['additional_req']
        p.is_expertise = data['is_expertise']
        p.save()

        log_object(get_current_user(), p, 2, 'Edited')

        return p


    def clean(self):
        data = self.cleaned_data

        if data.get('is_expertise') and data['pid'] == '':
                raise forms.ValidationError("Please provide your Expertise Grant project identifcation number")
            
        return data
