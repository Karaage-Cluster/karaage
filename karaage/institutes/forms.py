from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from karaage.people.models import Institute, Person
from karaage.projects.utils import pid_unique

class InstituteForm(forms.ModelForm):
    delegate = forms.ModelChoiceField(queryset=Person.active.select_related(), required=False)
    active_delegate = forms.ModelChoiceField(queryset=Person.active.select_related(), required=False)
    sub_delegates = forms.ModelMultipleChoiceField(
        queryset=Person.active.select_related(), required=False, 
        widget=FilteredSelectMultiple('Sub Delegates', False))


    def clean_saml_entityid(self):
        if self.cleaned_data['saml_entityid'] == "":
            return None
        return self.cleaned_data['saml_entityid']

    class Meta:
        model = Institute

    def clean_name(self):
        name = self.cleaned_data['name']
        if pid_unique(name):
            return name
        raise forms.ValidationError(u'Institute name already in system')

