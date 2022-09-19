# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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
from django.conf import settings

from karaage.institutes.models import Institute


def build_login_url(request, entityid=None):
    url = settings.AAF_RAPID_CONNECT_URL
    if entityid:
        url += "?entityID=%s" % entityid
    return url


def get_institute_from_token(verified_jwt):
    attrs = verified_jwt["https://aaf.edu.au/attributes"]
    value_list = attrs["edupersonscopedaffiliation"].split(";")
    value_list = [item for item in value_list if item]
    try:
        institute = Institute.objects.get(saml_scoped_affiliation__in=value_list)
    except Institute.DoesNotExist:
        institute = None
    return institute


def add_token_data(person, verified_jwt):
    attrs = verified_jwt["https://aaf.edu.au/attributes"]

    institute = get_institute_from_token(verified_jwt)
    if institute is None:
        return "ERR", f"No institute could be found for {attrs['edupersonscopedaffiliation']}"

    # short_name and full_name cannot be None
    person.short_name = attrs["givenname"]
    person.full_name = attrs["cn"]

    # fill in mandatory attributes
    person.email = attrs["mail"]
    person.saml_id = attrs["edupersontargetedid"]
    person.institute = institute
    person.email_verified = True

    # save person
    person.save()
    return "OK", None


class AafInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=None, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = Institute.active.filter(saml_entityid__isnull=False)
        queryset = queryset.exclude(saml_entityid="")

        self.fields["institute"].queryset = queryset
