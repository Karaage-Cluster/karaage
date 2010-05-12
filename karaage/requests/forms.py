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

import datetime
from andsome.middleware.threadlocals import get_current_user
from andsome.widgets import CaptchaInput

from karaage.projects.models import Project
from karaage.people.models import Person
from karaage.machines.models import MachineCategory
from karaage.people.models import Institute
from karaage.people.forms import UserForm
from karaage.datastores import create_new_user
from karaage.util.helpers import check_password, create_password_hash, get_new_pid

from models import ProjectCreateRequest


class UserRegistrationForm(UserForm):
    tos = forms.BooleanField(required=False, label=u'I have read and agree to the <a href="/users/policy" target="_blank">Acceptable Use Policy</a>')
    imghash = forms.CharField(widget=forms.HiddenInput)
    imgtext = forms.CharField(label=u'Text from the image', widget=CaptchaInput())

    def save(self, request, project=None, account=True):

        data = self.cleaned_data
        
        hashed_pw = create_password_hash(data['password1'])
        del data['password1']
        del data['password2']
        request.session['user_data'] = data
        request.session['project'] = project
        request.session['account'] = account
        request.session['password'] = hashed_pw


    def clean_tos(self):
        """
        Validates that the user accepted the Terms of Service.
        
        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(u'You must agree to the terms to register')

    def clean_imgtext(self):
        import sha
        SALT = settings.SECRET_KEY[:20]
        data = self.cleaned_data
        
        if not data['imghash'] or not data['imgtext']:
            raise forms.ValidationError(u'Error')
        if data['imghash'] == sha.new(SALT+data['imgtext'].upper()).hexdigest():
            
            return self.cleaned_data['imgtext']

        raise forms.ValidationError(u'Please type the code shown')


    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            p = Person.objects.get(user__email=email)
        except:
            p = None
        if p is not None:
            raise forms.ValidationError(u'Account with this email already exists. Please email accounts@vpac.org to reinstate your account')

        return email


class ProjectRegistrationForm(UserRegistrationForm):
    """
    Form used for users without accounts to register user and project at once
    """
    project_name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={ 'size':60 }))
    project_institute = forms.ModelChoiceField(queryset=Institute.valid.all())
    project_description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), help_text="Include any information about any grants you have received. Please keep this brief")
    additional_req = forms.CharField(label="Additional requirements", widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), help_text=u"Do you have any special requirements?", required=False)

    def save(self):

        data = self.cleaned_data

        project = Project(
            name=data['project_name'],
            description=data['project_description'],
            institute=data['project_institute'],
            is_approved=False,
            is_active=False,
            is_expertise=False,
            additional_req=data['additional_req'],
            start_date=datetime.datetime.today(),
            end_date=datetime.datetime.today() + datetime.timedelta(days=365),
        )
        
        project.pid = get_new_pid(data['project_institute'], False)

        person = create_new_user(data)
        
        project.machine_category = MachineCategory.objects.get_default()
        project.machine_categories.add(MachineCategory.objects.get_default())
        project.save()
        project.leaders.add(person)
        
        project_request = ProjectCreateRequest.objects.create(
            project=project,
            person=person,
            needs_account=data['needs_account']
        )

        return project_request
        


