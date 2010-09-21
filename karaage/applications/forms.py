from django import forms
from django.conf import settings
from django.contrib.auth.models import User

from karaage.applications.models import UserApplication, Applicant
from karaage.people.forms import UsernamePasswordForm
from karaage.util.helpers import check_password
from karaage.constants import TITLES
from karaage.people.models import Institute
from karaage.validators import username_re


class ApplicantForm(forms.ModelForm):
   # password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password')
   # password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label=u'Password (again)') 
    password1 = forms.CharField(widget=forms.PasswordInput(), label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label=u'Password (again)') 

    class Meta:
        model = Applicant

    def clean_username(self):

        username = self.cleaned_data['username']
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

    def clean(self):
        from karaage.util.helpers import create_password_hash
        super(self.__class__, self).clean()
        if 'password1' in self.cleaned_data:
            self.cleaned_data['password'] = create_password_hash(self.cleaned_data['password1'])
            print self.cleaned_data
        return self.cleaned_data



class UserApplicationForm(forms.ModelForm):
    aup = forms.BooleanField(label=u'I have read and agree to the <a href="%s" target="_blank">Acceptable Use Policy</a>' % settings.AUP_URL, 
                             error_messages={'required': 'You must accept to proceed.'})

    class Meta:
        model = UserApplication
        exclude = ['submitted_date', 'state', 'project', 'make_leader', 'content_type', 'object_id']


class AdminUserApplicationForm(forms.ModelForm):

    class Meta:
        model = UserApplication        
        exclude = ['submitted_date', 'state',]

class LeaderUserApplicationForm(forms.ModelForm):
    class Meta:
        model = UserApplication
        fields = ['make_leader',]

