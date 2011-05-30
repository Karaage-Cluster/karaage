from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from karaage.people.models import Institute, Person
from karaage.projects.models import Project

class InstituteForm(forms.ModelForm):

    def clean_saml_entityid(self):
        if self.cleaned_data['saml_entityid'] == "":
            return None
        return self.cleaned_data['saml_entityid']

    class Meta:
        model = Institute
        exclude = ('delegates',)

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            project = Project.objects.get(pid=name)
            raise forms.ValidationError(u'Institute name already in system')
        except Project.DoesNotExist:
            return name
