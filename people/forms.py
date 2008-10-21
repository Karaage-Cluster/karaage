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
from accounts.util.helpers import create_new_user, create_account, check_password
from accounts.validators import username_re

class UserForm(forms.Form):
    username = forms.CharField(label=u"Requested username", max_length=30, help_text=u"30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)')
    machine_category = forms.ModelChoiceField(queryset=MachineCategory.objects.all(), initial=1, required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label=u"Default Project", required=False)
    title = forms.ChoiceField(choices=TITLES)
    first_name = forms.CharField()
    last_name = forms.CharField()
    position = forms.CharField()
    institute = forms.ModelChoiceField(queryset=Institute.valid.all())
    department = forms.CharField()
    telephone = forms.CharField(label=u"Office Telephone")
    mobile = forms.CharField(required=False)
    fax = forms.CharField(required=False)
    address = forms.CharField(label=u"Mailing Address", required=False, widget=forms.Textarea())
    country = forms.ChoiceField(choices=COUNTRIES, initial='AU')
    website = forms.URLField(required=False)
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
                project_id = project.pid
            else:
                project_id = None

            if data['needs_account']:
                machine_category = data['machine_category']
                create_account(user.id, project_id, machine_category.id)

            # Since adding with this method is only done with admin
            user.activate()

        else:
            LogEntry.objects.create(
                user=get_current_user(),
                content_type=ContentType.objects.get_for_model(user.__class__),
                object_id=user.id, object_repr=user.__str__(), action_flag=2,
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



class ShellForm(forms.Form):

    shell = forms.ChoiceField(choices=settings.SHELLS)

    def save(self, user=None):

        if user is None:
            user = get_current_user().get_profile()


        from accounts.ldap_utils.ldap_users import change_shell
        change_shell(user, self.cleaned_data['shell'])
