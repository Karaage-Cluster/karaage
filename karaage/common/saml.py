# Copyright 2013-2015 VPAC
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

import six

from django.conf import settings
from django import forms
from karaage.institutes.models import Institute


def is_saml_session(request):
    if 'HTTP_SHIB_SESSION_ID' not in request.META:
        return False
    if not request.META['HTTP_SHIB_SESSION_ID']:
        return False
    return True


def parse_attributes(request):
    shib_attrs = {}
    error = False
    for header, attr in settings.SHIB_ATTRIBUTE_MAP.items():
        required, name = attr
        values = request.META.get(header, None)
        value = None
        if values:
            # If multiple attributes releases just care about the 1st one
            try:
                value = values.split(';')[0]
            except:
                value = values

        shib_attrs[name] = value
        if not value or value == '':
            if required:
                error = True
    return shib_attrs, error


def build_shib_url(request, target, entityid=None):
    url_base = 'https://%s' % request.get_host()
    shib_url = "%s%s" % (
        url_base, getattr(
            settings, 'SHIB_HANDLER_LOGIN', '/Shibboleth.sso/Login'))
    if not target.startswith('http'):
        target = url_base + target

    url = '%s?target=%s' % (shib_url, target)
    if entityid:
        url += '&entityID=%s' % entityid
    return url


def logout_url(request):
    url_base = 'https://%s' % request.get_host()
    url = "%s%s" % (
        url_base, getattr(
            settings, 'SHIB_HANDLER_LOGOUT', '/Shibboleth.sso/Logout'))
    return url


def add_saml_data(person, request):
    attrs, error = parse_attributes(request)

    # fill name if it was supplied
    if 'first_name' in attrs and attrs['first_name'] is not None:
        person.short_name = attrs['first_name']
        if 'last_name' in attrs and attrs['last_name'] is not None:
            person.full_name = six.u("%s %s") % (
                attrs['first_name'], attrs['last_name'])

    # short_name and full_name cannot be None
    if person.short_name is None:
        person.short_name = ""
    if person.full_name is None:
        person.full_name = ""

    # fill uid if it was supplied
    person.username = attrs.get('uid', person.username) \
        or person.username

    # fill telephone if supplied
    person.telephone = attrs.get('telephone', person.telephone) \
        or person.telephone

    # fill in mandatory attributes
    person.email = attrs['email']
    person.saml_id = attrs['persistent_id']
    person.institute = Institute.objects.get(saml_entityid=attrs['idp'])
    person.email_verified = True

    # save person
    person.save()
    return person


class SAMLInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=None, required=True)

    def __init__(self, *args, **kwargs):
        super(SAMLInstituteForm, self).__init__(*args, **kwargs)

        queryset = Institute.active.filter(saml_entityid__isnull=False)
        queryset = queryset.exclude(saml_entityid="")

        self.fields['institute'].queryset = queryset
