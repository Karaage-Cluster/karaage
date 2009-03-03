from django import forms
from django.conf import settings

import datetime
from django_common.middleware.threadlocals import get_current_user
from django_common.widgets import CaptchaInput

from karaage.projects.models import Project
from karaage.machines.models import MachineCategory
from karaage.people.models import Institute
from karaage.people.forms import UserForm
from karaage.datastores import create_new_user
from karaage.util.helpers import check_password, create_password_hash, get_new_pid

from models import ProjectCreateRequest


class UserRegistrationForm(UserForm):
    tos = forms.BooleanField(required=False, label=u'I have read and agree to the <a href="/users/policy" target="_blank">Acceptable Use Policy</a>')
    imghash = forms.CharField(widget=forms.HiddenInput)
    imgtext = forms.CharField(label=u'Text from the image', widget=CaptchaInput())

    def save(self, request, project=None, account=True):

        data = self.cleaned_data
        
        hashed_pw = create_password_hash(data['password1'])
        del data['password1']
        del data['password2']
        request.session['user_data'] = data
        request.session['project'] = project
        request.session['account'] = account
        request.session['password'] = hashed_pw


    def clean_tos(self):
        """
        Validates that the user accepted the Terms of Service.
        
        """
        if self.cleaned_data.get('tos', False):
            return self.cleaned_data['tos']
        raise forms.ValidationError(u'You must agree to the terms to register')

    def clean_imgtext(self):
        import sha
        SALT = settings.SECRET_KEY[:20]
        data = self.cleaned_data
        
        if not data['imghash'] or not data['imgtext']:
            raise forms.ValidationError(u'Error')
        if data['imghash'] == sha.new(SALT+data['imgtext'].upper()).hexdigest():
            
            return self.cleaned_data['imgtext']

        raise forms.ValidationError(u'Please type the code shown')


class ProjectRegistrationForm(UserRegistrationForm):
    """
    Form used for users without accounts to register user and project at once
    """
    pid = forms.CharField(label="PIN", max_length=10, required=False, help_text="If yes, please provide Project Identification Number")
    project_name = forms.CharField(label="Project Title", widget=forms.TextInput(attrs={ 'size':60 }))
    project_institute = forms.ModelChoiceField(queryset=Institute.valid.all())
    project_description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), help_text="Include any information about any grants you have received. Please keep this brief")
    additional_req = forms.CharField(label="Additional requirements", widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), help_text=u"Do you have any special requirements?", required=False)
    is_expertise = forms.BooleanField(required=False, label=u"Is this a current VPAC funded Expertise or Education Project?")
    machine_categories = forms.ModelMultipleChoiceField(queryset=MachineCategory.objects.all, widget=forms.CheckboxSelectMultiple)

    def save(self):

        data = self.cleaned_data

        project = Project(
            name=data['project_name'],
            description=data['project_description'],
            institute=data['project_institute'],
            is_approved=False,
            is_active=False,
            is_expertise=data['is_expertise'],
            additional_req=data['additional_req'],
            start_date=datetime.datetime.today(),
            end_date=datetime.datetime.today() + datetime.timedelta(days=365),
            machine_categories=data['machine_categories'],
        )

        if data['is_expertise']:
            project.pid = data['pid']
        else:
            project.pid = get_new_pid(data['institute'], data['is_expertise'])

        p = create_new_user(data)

        project.leader = user_request.person
        project.save()
        
        project_request = ProjectCreateRequest.objects.create(
            project=project,
            person=p,
            needs_account=data['needs_account']
        )

        return project_request

        
    def clean(self):
        data = self.cleaned_data

        super(ProjectRegistrationForm, self).clean()

        if data.get('is_expertise') and data['pid'] == '':
                raise forms.ValidationError("Please provide your Expertise Grant project identifcation number")
            
        return data                        

    def clean_project(self):
        return self.cleaned_data['project']
    


