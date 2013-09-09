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

from django.conf import settings
from django.shortcuts import render_to_response
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
    shib_url = "%s%s" % (url_base, getattr(settings, 'SHIB_HANDLER', '/Shibboleth.sso/DS'))
    if not target.startswith('http'):
        target = url_base + target

    url = '%s?target=%s' % (shib_url, target)
    if entityid:
        url += '&entityID=%s' % entityid
    return url


def logout_url(request):
    url_base = 'https://%s' % request.get_host()
    url = "%s%s" % (url_base, getattr(settings, 'SHIB_HANDLER', '/Shibboleth.sso/Logout'))
    return url


def add_saml_data(person, request):
    attrs, error = parse_attributes(request)
    person.short_name = attrs['first_name']
    person.full_name = u"%s %s" % (attrs['first_name'], attrs['last_name'])
    person.email = attrs['email']
    person.saml_id = attrs['persistent_id']
    person.telephone = attrs.get('telephone', None)
    person.institute = Institute.objects.get(saml_entityid=attrs['idp'])
    person.email_verified = True
    person.save()
    return person


class SAMLInstituteForm(forms.Form):
    institute = forms.ModelChoiceField(queryset=Institute.active.filter(saml_entityid__isnull=False).exclude(saml_entityid=""), required=True)
