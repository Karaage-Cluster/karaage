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
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm

from andsome.middleware.threadlocals import get_current_user
from andsome.util import is_password_strong

from karaage.people.models import Person, Group
from karaage.people.utils import validate_username, UsernameException
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project
from karaage.constants import TITLES, COUNTRIES


class PersonForm(forms.Form):
    title = forms.ChoiceField(choices=TITLES, required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    position = forms.CharField(required=False)
    email = forms.EmailField()
    department = forms.CharField(required=False)
    supervisor = forms.CharField(required=False)
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
    fax = forms.CharField(required=False)
    address = forms.CharField(label=u"Mailing Address", required=False, widget=forms.Textarea())
    country = forms.ChoiceField(choices=COUNTRIES, initial='AU', required=False)

    def save(self, person):
        data = self.cleaned_data
    
        person.first_name = data['first_name']
        person.last_name = data['last_name']
        person.email = data['email']
        person.title = data['title']
        person.position = data['position']
        person.supervisor = data['supervisor']
        person.department = data['department']
        person.telephone = data['telephone']
        person.mobile = data['mobile']
        person.fax = data['fax']
        person.address = data['address']
        person.country = data['country']
        person.user.save()
        person.save()
        return person


class AdminPersonForm(PersonForm):
    institute = forms.ModelChoiceField(queryset=Institute.active.all())
    comment = forms.CharField(widget=forms.Textarea(), required=False)
    expires = forms.DateField(widget=AdminDateWidget, required=False)
    is_staff = forms.BooleanField(help_text="Designates whether the user can log into this admin site.", required=False)
    is_superuser = forms.BooleanField(help_text="Designates that this user has all permissions without explicitly assigning them.", required=False)
    is_systemuser = forms.BooleanField(help_text="Designates that this user is a sytem user only.", required=False)

    def save(self, person):
        data = self.cleaned_data

        person.first_name = data['first_name']
        person.last_name = data['last_name']
        person.email = data['email']
        person.title = data['title']
        person.position = data['position']
        person.supervisor = data['supervisor']
        person.department = data['department']
        person.institute = data['institute']
        person.telephone = data['telephone']
        person.mobile = data['mobile']
        person.fax = data['fax']
        person.address = data['address']
        person.country = data['country']
        person.expires = data['expires']
        person.comment = data['comment']
        person.is_systemuser = data['is_systemuser']
        person.user.is_staff = data['is_staff']
        person.user.is_superuser = data['is_superuser']
        person.user.save()
        person.save()
        return person


class UsernamePasswordForm(forms.Form):
    username = forms.CharField(label=u"Requested username", max_length=16, help_text=u"16 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            validate_username(username)
        except UsernameException, e:
            raise forms.ValidationError(e.message)
            
        return username
    
    def clean_password2(self):
        data = self.cleaned_data

        if data.get('password1') and data.get('password2'):
        
            if data['password1'] != data['password2']:
                raise forms.ValidationError(u'You must type the same password each time')

            if not is_password_strong(data['password1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (uppercase, lowercase), numbers and is at least 8 characters long.')

            return data


class AddPersonForm(AdminPersonForm, UsernamePasswordForm):
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label=u"Default Project", required=False)
    needs_account = forms.BooleanField(required=False, label=u"Do you require a cluster account", help_text=u"eg. Will you be working on the project yourself")

    def save(self, person=None):
    
        data = self.cleaned_data
                
        if person is None:
            person = Person.create(data)
            
            # Since adding with this method is only done with admin
            person.activate()

            if data['needs_account'] and data['project']:
                add_user_to_project(person, data['project'])

        person = super(self.__class__, self).save(person)
        return person


class AdminPasswordChangeForm(forms.Form):
    new1 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password')
    new2 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def clean(self):
        data = self.cleaned_data

        if data.get('new1') and data.get('new2'):

            if data['new1'] != data['new2']:
                raise forms.ValidationError(u'You must type the same password each time')
            if not is_password_strong(data['new1'], data.get('old', None)):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (uppercase, lowercase), numbers and is at least 8 characters long.')
            return data

    def save(self, person):
        data = self.cleaned_data
        person.set_password(data['new1'])


class PasswordChangeForm(AdminPasswordChangeForm):
    old = forms.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        person = get_current_user().get_profile()
        
        from django.contrib.auth import authenticate
        user = authenticate(username=person.user.username, password=self.cleaned_data['old'])
        if user is None:
            raise forms.ValidationError(u'Your old password was incorrect')

        return self.cleaned_data['old']


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class SetPasswordForm(BaseSetPasswordForm):
    
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        if not is_password_strong(password1):
            raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (uppercase, lowercase), numbers and is at least 8 characters long.')
                        
        return password1

    def save(self, commit=True):
        person = self.user.get_profile()
        person.set_password(self.cleaned_data['new_password1'])
        return self.user


class PasswordResetForm(BasePasswordResetForm):

    email = forms.ModelChoiceField(queryset=Person.active.all(), label="Select person")

    def clean_email(self):
        email = self.cleaned_data["email"].email
        self.users_cache = User.objects.filter(
            email__iexact=email,
            is_active=True
        )
        if len(self.users_cache) == 0:
            raise forms.ValidationError("That e-mail address doesn't have an associated user account. Are you sure you've registered?")
        
        return email


class AdminGroupForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()

    def __init__(self, *args, **kwargs):
        # Make PID field read only if we are editing a project
        self.instance = kwargs.pop('instance', None)
        super(AdminGroupForm, self).__init__(*args, **kwargs)
        if self.instance is not None:
            self.initial = self.instance.__dict__
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].help_text = "You can't change the name of an existing group"

    def save(self, group=None):
        data = self.cleaned_data

        if self.instance is None:
            group = Group()
            group.name = data['name']

        group.description = data['description']
        group.save()

        return group

