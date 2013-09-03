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
from karaage.institutes.models import Institute


def add_saml_data(person, request):
    attrs, error = parse_attributes(request.META)
    person.first_name = attrs['first_name']
    person.last_name = attrs['last_name']
    person.email = attrs['email']
    person.saml_id = attrs['persistent_id']
    person.telephone = attrs.get('telephone', None)
    person.institute = Institute.objects.get(saml_entityid=attrs['idp'])
    person.email_verified = True
    person.save()
    return person


class SAMLInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.filter(saml_entityid__isnull=False).exclude(saml_entityid=""), required=True)
