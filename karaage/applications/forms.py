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
from django.contrib.auth.models import User
from django.db.models import Q

from andsome.util import is_password_strong
from captcha.fields import CaptchaField

from karaage.applications.models import UserApplication, ProjectApplication, Applicant
from karaage.people.models import Person, Institute
from karaage.people.forms import UsernamePasswordForm
from karaage.constants import TITLES
from karaage.projects.models import Project
from karaage.validators import username_re

APP_CHOICES = (
    ('U', 'Join an existing project'),
    ('P', 'Apply to start a new project'),
)

class StartInviteApplicationForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.all())

class StartApplicationForm(StartInviteApplicationForm):
    application_type = forms.ChoiceField(choices=APP_CHOICES, widget=forms.RadioSelect())

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant

class UserApplicantForm(ApplicantForm):

    def __init__(self, *args, **kwargs):
        super(UserApplicantForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'].label = 'Requested username'
        self.fields['username'].required = True
        self.fields['institute'].required = True

    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)') 
    institute = forms.ModelChoiceField(queryset=Institute.active.filter(Q(saml_entityid="") | Q(saml_entityid__isnull=True)))

    def clean_username(self):

        username = self.cleaned_data['username']
        if username:
            if not username.islower():
                raise forms.ValidationError(u'Username must be all lowercase')
 
            if not username_re.search(username):
                raise forms.ValidationError(u'Usernames can only contain letters, numbers and underscores')

            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                user = None
        
            if user is not None:
                raise forms.ValidationError(u'The username is already taken. Please choose another. If this was the name of your old account please email %s' % settings.ACCOUNTS_EMAIL)
        return username
    
    def clean_password2(self):
        data = self.cleaned_data

        if data.get('password1') and data.get('password2'):
        
            if data['password1'] != data['password2']:
                raise forms.ValidationError(u'You must type the same password each time')

            if not is_password_strong(data['password1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (upercase, lowercase), numbers and is at least 8 characters long.')

            return data

    def clean_email(self):
        email = self.cleaned_data['email']
        users = Person.active.filter(user__email__exact=email)
        if users:
            raise forms.ValidationError(u'An account with this email already exists. Please email %s' % settings.ACCOUNTS_EMAIL)
        return email


class UserApplicationForm(forms.ModelForm):
    aup = forms.BooleanField(label=u'I have read and agree to the <a href="%s" target="_blank">Acceptable Use Policy</a>' % settings.AUP_URL, 
                             error_messages={'required': 'You must accept to proceed.'})

    def __init__(self, *args, **kwargs):
        captcha = kwargs.pop('captcha', False)
        super(UserApplicationForm, self).__init__(*args, **kwargs)
        if captcha:
            self.fields['captcha'] = CaptchaField(label=u'CAPTCHA', help_text=u"Please enter the text displayed in the imge above.")

    class Meta:
        model = UserApplication
        exclude = ['submitted_date', 'state', 'project', 'make_leader', 'content_type', 'object_id']


class ProjectApplicationForm(forms.ModelForm):
    name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={ 'size':60 }))
    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }))
    additional_req = forms.CharField(label="Additional requirements", widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), help_text=u"Do you have any special requirements?", required=False)
    aup = forms.BooleanField(label=u'I have read and agree to the <a href="%s" target="_blank">Acceptable Use Policy</a>' % settings.AUP_URL, 
                             error_messages={'required': 'You must accept to proceed.'})

    
    def __init__(self, *args, **kwargs):
        captcha = kwargs.pop('captcha', False)
        super(ProjectApplicationForm, self).__init__(*args, **kwargs)
        if captcha:
            self.fields['captcha'] = CaptchaField(label=u'CAPTCHA', help_text=u"Please enter the text displayed in the imge above.")

    class Meta:
        model = ProjectApplication
        exclude = ['submitted_date', 'state', 'content_type', 'object_id']

class LeaderInviteUserApplicationForm(forms.ModelForm):
    email = forms.EmailField()
    
    def __init__(self, *args, **kwargs):
        super(LeaderInviteUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['header_message'].required = True

    class Meta:
        model = UserApplication
        fields = ['email', 'project', 'make_leader', 'header_message']

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            person = Person.active.get(user__email=email)
        except Person.MultipleObjectsReturned:
            raise forms.ValidationError(u'Multiple users with this email exist. Please add manually as no way to invite.')
        except Person.DoesNotExist:
            pass

        return email


class AdminInviteUserApplicationForm(LeaderInviteUserApplicationForm):

    def __init__(self, *args, **kwargs):
        super(AdminInviteUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['project'].required = True
            


class LeaderApproveUserApplicationForm(forms.ModelForm):

    class Meta:
        model = UserApplication
        fields = ['make_leader', 'needs_account',]

    def __init__(self, *args, **kwargs):
        super(LeaderApproveUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['needs_account'].label = u"Does this person require a cluster account?"
        self.fields['needs_account'].help_text = u"Will this person be working on the project?"


class ApproveProjectApplicationForm(forms.ModelForm):

    class Meta:
        model = ProjectApplication
        fields = ['needs_account',]

    def __init__(self, *args, **kwargs):
        super(ApproveProjectApplicationForm, self).__init__(*args, **kwargs)
        self.fields['needs_account'].label = u"Does this person require a cluster account?"
        self.fields['needs_account'].help_text = u"Will this person be working on the project?"


class AdminApproveProjectApplicationForm(ApproveProjectApplicationForm):
    pid = forms.CharField(label="Project ID", help_text="Leave blank for auto generation", required=False)
   
    def clean_pid(self):
        pid = self.cleaned_data['pid']
        try:
            institute = Institute.objects.get(name=pid)
            raise forms.ValidationError(u'Project ID already in system')
        except Institute.DoesNotExist:
            pass
        try:
            project = Project.objects.get(pid=pid)
            raise forms.ValidationError(u'Project ID already in system')
        except Project.DoesNotExist:
            pass
        return pid
