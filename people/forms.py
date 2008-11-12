from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

import datetime
from django_common.middleware.threadlocals import get_current_user

from karaage.people.models import Institute, Person
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, UserAccount
from karaage.constants import TITLES, STATES, COUNTRIES, DATE_FORMATS
from karaage.datastores import create_new_user, create_account
from karaage.util.helpers import check_password
from karaage.validators import username_re


class BaseUserForm(forms.Form):
    title = forms.ChoiceField(choices=TITLES)
    first_name = forms.CharField()
    last_name = forms.CharField()
    position = forms.CharField()
    email = forms.EmailField()
    department = forms.CharField()
    telephone = forms.CharField(label=u"Office Telephone")
    mobile = forms.CharField(required=False)
    fax = forms.CharField(required=False)
    address = forms.CharField(label=u"Mailing Address", required=False, widget=forms.Textarea())
    country = forms.ChoiceField(choices=COUNTRIES, initial='AU')
    website = forms.URLField(required=False)

    def save(self, person):
        data = self.cleaned_data
    
        person.first_name = data['first_name']
        person.last_name = data['last_name']
        person.email = data['email']
        person.title = data['title']
        person.position = data['position']
        person.department =data['department']
        person.telephone = data['telephone']
        person.mobile = data['mobile']
        person.fax = data['fax']
        person.address = data['address']
        person.country = data['country']
        person.website = data['website']
        person.save()
        person.user.save()

        return person


class UserForm(BaseUserForm):
    username = forms.CharField(label=u"Requested username", max_length=30, help_text=u"30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)')
    machine_category = forms.ModelChoiceField(queryset=MachineCategory.objects.all(), initial=1, required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label=u"Default Project", required=False)
    institute = forms.ModelChoiceField(queryset=Institute.valid.all())
    comment = forms.CharField(widget=forms.Textarea(), required=False)
    needs_account = forms.BooleanField(required=False, label=u"Do you require a VPAC computer account", help_text=u"eg. Will you be working on the project yourself")
    expires = forms.DateField(widget=forms.TextInput(attrs={ 'class':'vDateField' }), required=False)

    def clean_username(self):

        username = self.cleaned_data['username']
        if not username.islower():
            raise forms.ValidationError(u'Username must be all lowercase')
 
        if not username_re.search(username):
            raise forms.ValidationError(u'Usernames can only contain letters, numbers and underscores')

        try:
            user = User.objects.get(username__exact=username)
        except:
            try:
                user_account = UserAccount.objects.get(username__exact=username, machine_category=machine_category, date_deleted__isnull=True)
            except:
                return username

        raise forms.ValidationError(u'The username is already taken. Please choose another. If this was the name of your old VPAC account please email accounts@vpac.org')

    
    def clean(self):
        data = self.cleaned_data
        
        if data['needs_account']:
            if not data.get('machine_category'):
                raise forms.ValidationError(u'To make an account you must select a machine category.')

        if data.get('password1') and data.get('password2'):
        
            if data['password1'] != data['password2']:
                raise forms.ValidationError(u'You must type the same password each time')

            if not check_password(data['password1']):
                raise forms.ValidationError(u'Passwords must be at least 6 characters and contain at least one digit')

            return data
    
    def save(self, user=None):

        
        data = self.cleaned_data
                
        if user is None:
            user = create_new_user(data)
            
            if data['project'] is not None:
                project = data['project']
                project.users.add(user)
            else:
                project = None

            # Since adding with this method is only done with admin
            user.activate()

            if data['needs_account']:
                machine_category = data['machine_category']
                create_account(user, project, machine_category)

        else:
            LogEntry.objects.create(
                user=get_current_user(),
                content_type=ContentType.objects.get_for_model(user.__class__),
                object_id=user.id, 
                object_repr=str(user),
                action_flag=2,
                change_message='Edit')

        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.title = data['title']
        user.position = data['position']
        user.department =data['department']
        user.institute = data['institute']
        user.telephone = data['telephone']
        user.mobile = data['mobile']
        user.fax = data['fax']
        user.address = data['address']
        user.country = data['country']
        user.website = data['website']
        user.expires = data['expires']
        # This is here so comment is not overriden when user changes detail.
        if 'comment' in self.data:
            user.comment = data['comment']
        user.user.save()
        user.save()

        return user


class AdminPasswordChangeForm(forms.Form):
    new1 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password')
    new2 = forms.CharField(widget=forms.PasswordInput(), label=u'New Password (again)')

    def clean(self):
        data = self.cleaned_data

        if data.get('new1') and data.get('new2'):

            if data['new1'] != data['new2']:
                raise forms.ValidationError(u'You must type the same password each time')
            if not check_password(data['new1']):
                raise forms.ValidationError(u'Passwords must be at least 6 characters and contain at least one digit')
            return data

    def save(self, person):        
        data = self.cleaned_data
        person.set_password(data['new1'])



class PasswordChangeForm(AdminPasswordChangeForm):
    old = forms.CharField(widget=forms.PasswordInput(), label='Old password')

    def clean_old(self):
        person = get_current_user().get_profile()
        if not person.check_password(self.cleaned_data['old']):
            raise forms.ValidationError(u'Your old password was incorrect')
        return self.cleaned_data['old']



class DelegateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields['active_delegate'] = forms.ModelChoiceField(label="Change to", queryset=Person.active.all())


    def save(self, institute):

        data = self.cleaned_data

        previous = institute.active_delegate

        institute.active_delegate = data['active_delegate']

        institute.save()
