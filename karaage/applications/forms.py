from django import forms
from django.conf import settings
from django.contrib.auth.models import User

from karaage.applications.models import UserApplication, ProjectApplication, Applicant
from karaage.people.models import Person
from karaage.people.forms import UsernamePasswordForm
from karaage.util.helpers import check_password
from karaage.constants import TITLES
from karaage.people.models import Institute
from karaage.validators import username_re


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant


class UserApplicantForm(ApplicantForm):

    def __init__(self, *args, **kwargs):
        super(UserApplicantForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'].required = True
        self.fields['institute'].required = True

    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)') 

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

            if not check_password(data['password1']):
                raise forms.ValidationError(u'Your password was found to be insecure, a good password has a combination of letters (upercase, lowercase), numbers and is at least 8 characters long.')

            return data

    def clean_email(self):
        email = self.cleaned_data['email']
        users = Person.active.filter(user__email__exact=email)
        if users:
            raise forms.ValidationError(u'An account with this email already exists. Please email %s' % settings.ACCOUNTS_EMAIL)
        return email

    def clean(self):
        from karaage.util.helpers import create_password_hash
        super(self.__class__, self).clean()
        if 'password1' in self.cleaned_data:
            self.cleaned_data['password'] = create_password_hash(self.cleaned_data['password1'])
        return self.cleaned_data



class UserApplicationForm(forms.ModelForm):
    aup = forms.BooleanField(label=u'I have read and agree to the <a href="%s" target="_blank">Acceptable Use Policy</a>' % settings.AUP_URL, 
                             error_messages={'required': 'You must accept to proceed.'})

    class Meta:
        model = UserApplication
        exclude = ['submitted_date', 'state', 'project', 'make_leader', 'content_type', 'object_id']


class ProjectApplicationForm(forms.ModelForm):
    
    class Meta:
        model = ProjectApplication
        exclude = ['submitted_date', 'state', 'content_type', 'object_id']

class LeaderInviteUserApplicationForm(forms.ModelForm):
    email = forms.EmailField()
    
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

