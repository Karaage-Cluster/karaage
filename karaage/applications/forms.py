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

import re

from django import forms
from django.conf import settings
from django.db.models import Q

from captcha.fields import CaptchaField

from karaage.applications.models import UserApplication, ProjectApplication, Applicant
from karaage.people.models import Person
from karaage.people.utils import validate_username, UsernameException
from karaage.institutes.models import Institute
from karaage.projects.models import Project

APP_CHOICES = (
    ('U', 'Join an existing project'),
    ('P', 'Apply to start a new project'),
)


def _clean_email(email):
    email_match_type = "exclude"
    email_match_list = []
    if hasattr(settings, 'EMAIL_MATCH_TYPE'):
        email_match_type = settings.EMAIL_MATCH_TYPE
    if hasattr(settings, 'EMAIL_MATCH_LIST'):
        email_match_list = settings.EMAIL_MATCH_LIST

    found = False
    for string in email_match_list:
        m = re.search(string, email, re.IGNORECASE)
        if m is not None:
            found = True
            break

    message = "This email address cannot be used."
    if email_match_type == "include":
        if not found:
            raise forms.ValidationError(message)
    elif email_match_type == "exclude":
        if found:
            raise forms.ValidationError(message)
    else:
        raise forms.ValidationError("Oops. Nothing is valid. Sorry.")


class StartInviteApplicationForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.all())


class StartApplicationForm(StartInviteApplicationForm):
    application_type = forms.ChoiceField(choices=APP_CHOICES, widget=forms.RadioSelect())


class ApplicantForm(forms.ModelForm):
    telephone = forms.RegexField(
            "^[0-9a-zA-Z\.( )+-]+$", required=False, label=u"Office Telephone",
            error_messages={'invalid':
            'Telephone number may only contain digits, letter, hyphens, spaces, braces,  and the plus sign.'})
    mobile = forms.RegexField(
            "^[0-9a-zA-Z( )+-]+$",
            help_text=u"Used for emergency contact and password reset service.",
            required=False,
            error_messages={'invalid':
            'Telephone number may only contain digits, letter, hyphens, spaces, braces,  and the plus sign.'})

    class Meta:
        model = Applicant

    def clean_username(self):
        username = self.cleaned_data['username']
        if username:
            try:
                validate_username(username)
            except UsernameException, e:
                raise forms.ValidationError(e.args[0])
        
            return username


class UserApplicantForm(ApplicantForm):

    def __init__(self, *args, **kwargs):
        super(UserApplicantForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'].label = 'Requested username'
        self.fields['username'].required = True
        self.fields['institute'].required = True
        self.fields['telephone'].required = True

    institute = forms.ModelChoiceField(queryset=Institute.active.filter(Q(saml_entityid="") | Q(saml_entityid__isnull=True)))
    
    def clean_email(self):
        email = self.cleaned_data['email']
        users = Person.active.filter(user__email__exact=email)
        if users:
            raise forms.ValidationError(u'An account with this email already exists. Please email %s' % settings.ACCOUNTS_EMAIL)
        _clean_email(email)
        return email

    def save(self, commit=True):
        applicant = super(UserApplicantForm, self).save(commit=commit)
        if commit:
            applicant.save()
        return applicant


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
    name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}))
    additional_req = forms.CharField(label="Additional requirements", widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), help_text=u"Do you have any special requirements?", required=False)
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
            Person.active.get(user__email=email)
        except Person.MultipleObjectsReturned:
            raise forms.ValidationError(u'Multiple users with this email exist. Please add manually as no way to invite.')
        except Person.DoesNotExist:
            pass

        try:
            applicant = Applicant.objects.get(email=email)
        except Applicant.DoesNotExist:
            applicant = None

        if applicant:
            raise forms.ValidationError(u'Applicant with email %s already exists' % email)
        return email

        _clean_email(email)


class AdminInviteUserApplicationForm(LeaderInviteUserApplicationForm):

    def __init__(self, *args, **kwargs):
        super(AdminInviteUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['project'].required = True


class LeaderApproveUserApplicationForm(forms.ModelForm):

    class Meta:
        model = UserApplication
        fields = ['make_leader', 'needs_account']

    def __init__(self, *args, **kwargs):
        super(LeaderApproveUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['needs_account'].label = u"Does this person require a cluster account?"
        self.fields['needs_account'].help_text = u"Will this person be working on the project?"


class ApproveProjectApplicationForm(forms.ModelForm):

    class Meta:
        model = ProjectApplication
        fields = ['needs_account']

    def __init__(self, *args, **kwargs):
        super(ApproveProjectApplicationForm, self).__init__(*args, **kwargs)
        self.fields['needs_account'].label = u"Does this person require a cluster account?"
        self.fields['needs_account'].help_text = u"Will this person be working on the project?"


class AdminApproveProjectApplicationForm(ApproveProjectApplicationForm):
    pid = forms.CharField(label="Project ID", help_text="Leave blank for auto generation", required=False)
   
    def clean_pid(self):
        pid = self.cleaned_data['pid']
        try:
            Institute.objects.get(name=pid)
            raise forms.ValidationError(u'Project ID already in system')
        except Institute.DoesNotExist:
            pass
        try:
            Project.objects.get(pid=pid)
            raise forms.ValidationError(u'Project ID already in system')
        except Project.DoesNotExist:
            pass
        return pid
