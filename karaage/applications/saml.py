# Copyright 2007-2013 VPAC
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
import karaage.util.saml as saml

from karaage.applications.forms import UserApplicantForm
from karaage.institutes.models import Institute


def add_saml_data(applicant, request):
    attrs, error = saml.parse_attributes(request)
    applicant.short_name = attrs['first_name']
    applicant.full_name = u"%s %s" % (attrs['first_name'], attrs['last_name'])
    applicant.email = attrs['email']
    applicant.saml_id = attrs['persistent_id']
    applicant.telephone = attrs.get('telephone', None)
    applicant.institute = Institute.objects.get(saml_entityid=attrs['idp'])
    applicant.email_verified = True
    applicant.save()
    return applicant


class SAMLApplicantForm(UserApplicantForm):

    def __init__(self, *args, **kwargs):
        super(SAMLApplicantForm, self).__init__(*args, **kwargs)
        del self.fields['institute']


class SAMLInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.filter(saml_entityid__isnull=False).exclude(saml_entityid=""))
