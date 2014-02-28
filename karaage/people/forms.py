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
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm

from karaage.people.emails import send_reset_password_email
from karaage.people.models import Person, Group
from karaage.people.utils import validate_username_for_new_person, UsernameException
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.projects.utils import add_user_to_project
from karaage.common.constants import COUNTRIES
from karaage.common import get_current_person, is_password_strong

import ajax_select.fields


class PersonForm(forms.ModelForm):
#    title = forms.ChoiceField(choices=TITLES, required=False)
#    position = forms.CharField(required=False)
#    email = forms.EmailField()
#    department = forms.CharField(required=False)
#    supervisor = forms.CharField(required=False)
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
    fax = forms.CharField(required=False)
    address = forms.CharField(label=u"Mailing Address", required=False, widget=forms.Textarea())
    country = forms.ChoiceField(choices=COUNTRIES, initial='AU', required=False)

    class Meta:
        model = Person
        fields = ['short_name', 'full_name', 'email', 'title', 'position', 'supervisor',
                'department', 'telephone', 'mobile', 'fax', 'address', 'country' ]


class AdminPersonForm(PersonForm):
    institute = forms.ModelChoiceField(queryset=Institute.active.all())
    comment = forms.CharField(widget=forms.Textarea(), required=False)
    expires = forms.DateField(widget=AdminDateWidget, required=False)
    is_admin = forms.BooleanField(help_text="Designates whether the user can log into this admin site.", required=False)
    is_systemuser = forms.BooleanField(help_text="Designates that this user is a system process, not a person.", required=False)

    class Meta:
        model = Person
        fields = ['short_name', 'full_name', 'email', 'title', 'position', 'supervisor',
                'department', 'institute', 'telephone', 'mobile', 'fax', 'address', 'country',
                'expires', 'comment', 'is_systemuser', 'is_admin', ]


class AddPersonForm(AdminPersonForm):
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label=u"Default Project", required=False)
    needs_account = forms.BooleanField(required=False, label=u"Do you require a cluster account", help_text=u"eg. Will you be working on the project yourself")
    username = forms.CharField(label=u"Requested username", max_length=16, help_text=u"16 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            validate_username_for_new_person(username)
        except UsernameException, e:
            raise forms.ValidationError(e.args[0])
        return username

    def clean_password1(self):
        data = self.cleaned_data

        if data.get('password1'):
            if not is_password_strong(data['password1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (uppercase, lowercase), numbers and is at least 8 characters long.')

        return data['password1']

    def clean_password2(self):
        data = self.cleaned_data

        if data.get('password1') and data.get('password2'):
            if data['password1'] != data['password2']:
                raise forms.ValidationError(u'You must type the same password each time')

        return data['password2']

    def save(self):
        data = self.cleaned_data

        person = super(AddPersonForm, self).save(commit=False)
        person.username = data['username']
        person.is_admin = data['is_admin']
        person.is_active = True
        person.approved_by = get_current_person()
        person.set_password(data['password2'])
        person.save()

        if data['needs_account'] and data['project']:
            add_user_to_project(person, data['project'])

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
        person.save()


class PasswordChangeForm(AdminPasswordChangeForm):
    old = forms.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        person = get_current_person()

        person = Person.objects.authenticate(username=person.username, password=self.cleaned_data['old'])
        if person is None:
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


class AdminGroupForm(forms.Form):
    name = forms.RegexField("^%s$" % settings.GROUP_VALIDATION_RE, required=True,
            error_messages={'invalid': settings.GROUP_VALIDATION_ERROR_MSG})
    description = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(AdminGroupForm, self).__init__(*args, **kwargs)
        if self.instance is not None:
            self.initial = self.instance.__dict__

    def clean_name(self):
        name = self.cleaned_data["name"]
        groups = Group.objects.filter(name=name)
        if self.instance is not None:
            groups = groups.exclude(pk=self.instance.pk)
        if groups.count() > 0:
            raise forms.ValidationError("That group name already exists.")
        return name

    def save(self, group=None):
        data = self.cleaned_data

        if self.instance is None:
            group = Group()
            group.name = data['name']

        else:
            group = self.instance
            group.change_name(data['name'])

        group.description = data['description']
        group.save()

        return group

class AddGroupMemberForm(forms.Form):
    """ Add a user to a group form """
    person = ajax_select.fields.AutoCompleteSelectField('person', required=True, label="Add person")

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(AddGroupMemberForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        person = self.cleaned_data['person']
        self.instance.add_person(person)
        return self.instance
