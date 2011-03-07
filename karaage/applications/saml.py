from django import forms
from django_shibboleth.utils import parse_attributes

from karaage.applications.forms import UserApplicantForm
from karaage.people.models import Institute


def add_saml_data(applicant, request):
    attrs, error = parse_attributes(request.META)   
    applicant.first_name = attrs['first_name']
    applicant.last_name = attrs['last_name']
    applicant.email = attrs['email']
    applicant.saml_id = attrs['persistent_id']
    applicant.telephone = attrs.get('telephone', None)
    applicant.institute = Institute.objects.get(saml_entityid=attrs['idp'])
    applicant.save()
    return applicant


class SAMLUser:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def get_saml_user(request):
    attrs, error = parse_attributes(request.META)
    return SAMLUser(**attrs)


class SAMLApplicantForm(UserApplicantForm):

    def __init__(self, *args, **kwargs):
        super(SAMLApplicantForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['institute'].required = False
        self.fields['username'].label = 'Requested username'
        self.fields['username'].required = True

 
class SAMLInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.filter(saml_entityid__isnull=False))
