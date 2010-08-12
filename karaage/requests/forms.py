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
from captcha.fields import CaptchaField
from andsome.middleware.threadlocals import get_current_user

from karaage.projects.models import Project
from karaage.projects.utils import get_new_pid
from karaage.people.models import Person
from karaage.machines.models import MachineCategory
from karaage.people.models import Institute
from karaage.people.forms import AddUserForm
from karaage.datastores import create_new_user
from karaage.util.helpers import check_password, create_password_hash
from karaage.requests.models import ProjectCreateRequest


class UserRegistrationForm(AddUserForm):
    title = forms.ChoiceField(choices=TITLES)
    position = forms.CharField()
    department = forms.CharField()
    country = forms.ChoiceField(choices=COUNTRIES, initial='AU')
    telephone = forms.CharField(label=u"Office Telephone")

    tos = forms.BooleanField(required=False, label=u'I have read and agree to the <a href="%s" target="_blank">Acceptable Use Policy</a>'%(settings.AUP_URL))
    captcha = CaptchaField(label=u'CAPTCHA', help_text=u"Please enter the text displayed in the imge above.")

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

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            p = Person.objects.get(user__email=email)
        except Person.DoesNotExist:
            p = None
        if p is not None:
            raise forms.ValidationError(u'Account with this email already exists. Please email %s to reinstate your account'%(settings.ACCOUNTS_EMAIL))

        return email


class ProjectRegistrationForm(UserRegistrationForm):
    """
    Form used for users without accounts to register user and project at once
    """
    project_name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={ 'size':60 }))
    project_institute = forms.ModelChoiceField(queryset=Institute.active.all())
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
            additional_req=data['additional_req'],
            start_date=datetime.datetime.today(),
            end_date=datetime.datetime.today() + datetime.timedelta(days=365),
        )
        
        project.pid = get_new_pid(data['project_institute'])

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
        


