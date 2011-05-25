from django import forms

from karaage.people.models import Institute

class InstituteForm(forms.ModelForm):

    def clean_saml_entityid(self):
        if self.cleaned_data['saml_entityid'] == "":
            return None
        return self.cleaned_data['saml_entityid']

    class Meta:
        model = Institute

