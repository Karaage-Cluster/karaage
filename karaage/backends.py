# Copyright 2011, 2013-2015 VPAC
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

from django.contrib.auth.backends import ModelBackend

from karaage.people.models import Person
import tldap.ldap_passwd


class LDAPBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            person = Person.objects.get(username__exact=username)
        except Person.DoesNotExist:
            return None

        if person.legacy_ldap_password is None:
            return None

        if not tldap.ldap_passwd.check_password(
                password, person.legacy_ldap_password):
            return None

        # Success.
        person.set_password(password)
        person.save()

        return person
