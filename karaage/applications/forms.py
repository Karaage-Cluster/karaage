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
import ajax_select.fields

from django import forms
from django.conf import settings
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from captcha.fields import CaptchaField

from karaage.applications.models import Application, ProjectApplication, Applicant
from karaage.people.models import Person
from karaage.people.utils import validate_username, UsernameException
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.util import get_current_person

from andsome.util import is_password_strong

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


class StartApplicationForm(forms.Form):
    application_type = forms.ChoiceField(choices=APP_CHOICES, widget=forms.RadioSelect())


class ApplicantForm(forms.ModelForm):
    telephone = forms.RegexField(
            "^[0-9a-zA-Z\.( )+-]+$", required=True, label=u"Office Telephone",
            help_text=u"Used for emergency contact and password reset service.",
            error_messages={'invalid':
            'Telephone number may only contain digits, letter, hyphens, spaces, braces,  and the plus sign.'})
    mobile = forms.RegexField(
            "^[0-9a-zA-Z( )+-]+$",
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

    def clean_email(self):
        email = self.cleaned_data['email']
        users = Person.active.filter(user__email__exact=email)
        if users:
            raise forms.ValidationError(u'An account with this email already exists. Please email %s' % settings.ACCOUNTS_EMAIL)
        _clean_email(email)
        return email


class UserApplicantForm(ApplicantForm):

    def __init__(self, *args, **kwargs):
        super(UserApplicantForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'].label = 'Requested username'
        self.fields['username'].required = True
        self.fields['institute'].required = True

    institute = forms.ModelChoiceField(queryset=Institute.active.filter(Q(saml_entityid="") | Q(saml_entityid__isnull=True)))
    
    def save(self, commit=True):
        applicant = super(UserApplicantForm, self).save(commit=commit)
        if commit:
            applicant.save()
        return applicant

    class Meta:
        model = Applicant
        exclude = ['email']


class SAMLApplicantForm(UserApplicantForm):

    def __init__(self, *args, **kwargs):
        super(SAMLApplicantForm, self).__init__(*args, **kwargs)
        del self.fields['institute']

    class Meta:
        model = Applicant
        exclude = ['email', 'institute']


class CommonApplicationForm(forms.ModelForm):
    aup = forms.BooleanField(error_messages={'required': 'You must accept to proceed.'})
    application_type = forms.ChoiceField(choices=APP_CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super(CommonApplicationForm, self).__init__(*args, **kwargs)
        aup_url = getattr(settings, 'AUP_URL', None)
        if aup_url is None:
            aup_url = reverse('aup')
        self.fields['aup'].label = mark_safe(u'I have read and agree to the <a href="%s" target="_blank">Acceptable Use Policy</a>' % aup_url)

    class Meta:
        model = ProjectApplication
        fields = ['needs_account']


class NewProjectApplicationForm(forms.ModelForm):
    name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}))
    additional_req = forms.CharField(label="Additional requirements", widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), help_text=u"Do you have any special requirements?", required=False)

    def __init__(self, *args, **kwargs):
        super(NewProjectApplicationForm, self).__init__(*args, **kwargs)
        self.fields['machine_categories'].required = True

    class Meta:
        model = ProjectApplication
        fields = ['name', 'description', 'additional_req', 'machine_categories']


class ExistingProjectApplicationForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=Project.active.all())

    class Meta:
        model = ProjectApplication
        fields = ['project', 'make_leader']


class InviteUserApplicationForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.cleaned_data = None
        self.fields = None
        super(InviteUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['header_message'].required = True

    class Meta:
        model = ProjectApplication
        fields = ['email', 'make_leader', 'header_message']

    def clean_email(self):
        email = self.cleaned_data['email']

        query = Person.active.filter(user__email=email)
        if query.count() > 0:
            raise forms.ValidationError(u'E-Mail address is already in use.')

        query = Application.objects.filter(applicant__email=email).exclude(state__in=[Application.COMPLETED, Application.ARCHIVED, Application.DECLINED])
        if query.count() > 0:
            raise forms.ValidationError(u'Applicantion with email %s already exists' % email)

        _clean_email(email)
        return email

    def clean_project(self):
        project = self.cleaned_data['project']
        person = get_current_person()
        if project is not None:
            if not person in project.leaders.all():
                raise forms.ValidationError(u'You must be the project leader.')
        return project


class AdminInviteUserApplicationForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.cleaned_data = None
        self.fields = None
        super(AdminInviteUserApplicationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['header_message'].required = True

    class Meta:
        model = ProjectApplication
        fields = ['email', 'project', 'make_leader', 'header_message']

    def clean_email(self):
        email = self.cleaned_data['email']
        _clean_email(email)
        return email


class UnauthenticatedInviteUserApplicationForm(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField(label=u'CAPTCHA', help_text=u"Please enter the text displayed in the image above.")

    def clean_email(self):
        email = self.cleaned_data['email']

        query = Person.active.filter(user__email=email)
        if query.count() > 0:
            raise forms.ValidationError(u'E-Mail address is already in use. Do you already have an account?')

        query = Application.objects.filter(applicant__email=email).exclude(state__in=[Application.COMPLETED, Application.ARCHIVED, Application.DECLINED])
        if query.count() > 0:
            raise forms.ValidationError(u'Applicantion with email %s already exists' % email)

        _clean_email(email)
        return email


def ApproveApplicationFormGenerator(application, auth):
    if application.project is None:
        # new project
        include_fields = ['machine_categories', 'additional_req', 'needs_account']
    else:
        # existing project
        include_fields = ['make_leader', 'additional_req', 'needs_account']

    class ApproveApplicationForm(forms.ModelForm):
        additional_req = forms.CharField(label="Additional requirements", widget=forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10, 'cols': 40}), help_text=u"Do you have any special requirements?", required=False)

        class Meta:
            model = ProjectApplication
            fields = include_fields

        def __init__(self, *args, **kwargs):
            super(ApproveApplicationForm, self).__init__(*args, **kwargs)
            self.fields['needs_account'].label = u"Does this person require a cluster account?"
            self.fields['needs_account'].help_text = u"Will this person be working on the project?"
            if application.project is None:
                self.fields['machine_categories'].required = True

    return ApproveApplicationForm


def AdminApproveApplicationFormGenerator(application, auth):
    parent = ApproveApplicationFormGenerator(application, auth)
    if application.project is None:
        # new project
        include_fields = ['pid', 'machine_categories', 'additional_req', 'needs_account']
    else:
        # existing project
        include_fields = ['make_leader', 'additional_req', 'needs_account']

    class AdminApproveApplicationForm(parent):
        if application.project is None:
            pid = forms.CharField(label="Project ID", help_text="Leave blank for auto generation", required=False)
        if application.content_type.model == 'applicant':
            replace_applicant = ajax_select.fields.AutoCompleteSelectField('person', required=False, help_text="Do not set unless absolutely positive sure.")

        class Meta:
            model = ProjectApplication
            fields = include_fields

        def clean_pid(self):
            pid = self.cleaned_data['pid']
            if not pid:
                return pid
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

        def save(self, *args, **kwargs):
            if application.content_type.model == 'applicant':
                replace_applicant = self.cleaned_data['replace_applicant']
                if replace_applicant is not None:
                    self.instance.applicant = replace_applicant
            return super(AdminApproveApplicationForm, self).save(*args, **kwargs)

    return AdminApproveApplicationForm


class PersonSetPassword(forms.Form):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    new_password1 = forms.CharField(label=u"New password",
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=u"New password confirmation",
                                    widget=forms.PasswordInput)

    def __init__(self, person, *args, **kwargs):
        self.person = person
        super(PersonSetPassword, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if not is_password_strong(password1):
            raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (uppercase, lowercase), numbers and is at least 8 characters long.')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u"The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        self.person.set_password(self.cleaned_data['new_password1'])
        return self.person


class PersonVerifyPassword(forms.Form):
    """
    A form that lets a user verify his old password and updates it on all datastores.
    """
    password = forms.CharField(label="Existing password",
                                    widget=forms.PasswordInput)

    def __init__(self, person, *args, **kwargs):
        self.person = person
        super(PersonVerifyPassword, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        from django.contrib.auth import login, authenticate
        user = authenticate(username=self.person.user.username, password=password)

        if user is None:
            raise forms.ValidationError(u"Password is incorrect.")

        assert user == self.person.user

        if not user.is_active or self.person.is_locked():
            raise forms.ValidationError(u"Person is locked.")

        return password

    def save(self, commit=True):
        password = self.cleaned_data['password']
        self.person.set_password(password)
        self.person.save()
        return self.person
