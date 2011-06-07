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
from django.conf import settings

from andsome.middleware.threadlocals import get_current_user
from andsome.util import is_password_strong

from karaage.people.models import Institute, Person
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project
from karaage.constants import TITLES, COUNTRIES
from karaage.datastores import create_new_user
from karaage.validators import username_re


class PersonForm(forms.Form):
    title = forms.ChoiceField(choices=TITLES, required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    position = forms.CharField(required=False)
    email = forms.EmailField()
    department = forms.CharField(required=False)
    supervisor = forms.CharField(required=False)
    telephone = forms.CharField(label=u"Office Telephone", required=False)
    mobile = forms.CharField(required=False, help_text=u"Used for emergency contact and password reset service.")
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
        person.department =data['department']
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
        person.department =data['department']
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
        if not username.islower():
            raise forms.ValidationError(u'Username must be all lowercase')
 
        if not username_re.search(username):
            raise forms.ValidationError(u'Usernames can only contain letters, numbers and underscores')

        try:
            user = User.objects.get(username__exact=username)
        except:
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
    



class AddPersonForm(AdminPersonForm, UsernamePasswordForm):
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label=u"Default Project", required=False)
    needs_account = forms.BooleanField(required=False, label=u"Do you require a cluster account", help_text=u"eg. Will you be working on the project yourself")

    def save(self, person=None):
    
        data = self.cleaned_data
                
        if person is None:
            person = create_new_user(data)
            
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
                raise forms.ValidationError(u'Passwords must be at least 6 characters and contain at least one digit')
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
