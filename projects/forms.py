from django import forms
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
import datetime
from karaage.people.models import Institute, Person
from karaage.machines.models import MachineCategory
from models import Project
from karaage.constants import DATE_FORMATS
from django_common.middleware.threadlocals import get_current_user

from accounts.util.helpers import get_new_pid


class ProjectForm(forms.Form):
    pid = forms.CharField(max_length=10, required=False, help_text="If left blank the next available pid will be used")
    name = forms.CharField(widget=forms.TextInput(attrs={ 'size':60 }))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    institute = forms.ModelChoiceField(queryset=Institute.valid.all())
    additional_req = forms.CharField(widget=forms.Textarea(attrs={'class':'vLargeTextField', 'rows':10, 'cols':40 }), required=False)
    is_expertise = forms.BooleanField(required=False, help_text=u"Is this a current VPAC funded Expertise or Education Project?")
    leader = forms.ModelChoiceField(queryset=Person.active.all())
    start_date = forms.DateField(widget=forms.TextInput(attrs={ 'class':'vDateField' }), input_formats=DATE_FORMATS)
    end_date = forms.DateField(widget=forms.TextInput(attrs={ 'class':'vDateField' }), input_formats=DATE_FORMATS, required=False)
    machine_category = forms.ModelChoiceField(queryset=MachineCategory.objects.all(), initial=1)
    cap = forms.IntegerField(required=False)

    def save(self, p=None):
        data = self.cleaned_data

        if p is None:
            p = Project()
            if data['pid']:
                p.pid = data['pid']
            else:
                p.pid = get_new_pid(data['institute'], data['is_expertise'])
            p.is_active = True
            p.is_approved = True
            p.date_approved = datetime.datetime.today()
            approver = get_current_user()
            p.approved_by = approver.get_profile()

            LogEntry.objects.create(
                user=get_current_user(),
                content_type=ContentType.objects.get_for_model(p.__class__),
                object_id=p.pid,
                object_repr=p.pid,
                action_flag=1,
                change_message='Created'
            )
        else:
            LogEntry.objects.create(
                user=get_current_user(),
                content_type=ContentType.objects.get_for_model(p.__class__),
                object_id=p.pid,
                object_repr=p.pid,
                action_flag=2,
                change_message='Edited'
            )
            
        p.name = data['name']
        p.description = data['description']
        p.institute = data['institute']
        p.additional_req = data['additional_req']
        p.is_expertise = data['is_expertise']
        p.leader = data['leader']
        p.start_date = data['start_date']
        p.end_date = data['end_date']
        p.machine_category = data['machine_category']
        p.cap = data['cap']
        p.save()

        return p
            
    def clean_pid(self):
        if self.cleaned_data.get('pid'):
            try:
                project = Project.objects.get(pk=self.cleaned_data['pid'])
            except:
                return self.cleaned_data['pid']
            raise forms.ValidationError(u'PID already exists')

