# Copyright 2011 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

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
        self.fields['username'].label = 'Requested username'
        self.fields['username'].required = True
        del self.fields['institute']


class SAMLInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.filter(saml_entityid__isnull=False).exclude(saml_entityid=""))
