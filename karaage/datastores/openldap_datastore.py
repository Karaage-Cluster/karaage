# Copyright 2007-2010 VPAC
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

from placard.client import LDAPClient
from placard.exceptions import DoesNotExistException

from karaage.datastores import ldap_datastore


class PersonalDataStore(ldap_datastore.PersonalDataStore):
    
    def is_locked(self, person):
        super(ldap_datastore.PersonalDataStore, self).is_locked(person)

        conn = LDAPClient()
        try:
            ldap_user = conn.get_user('uid=%s' % person.username)
        except DoesNotExistException:
            return True

        return conn.is_locked('uid=%s' % person.username)

    def lock_user(self, person):
        super(ldap_datastore.PersonalDataStore, self).lock_user(person)
        
        conn = LDAPClient()
        conn.lock_user('uid=%s' % person.username)
        
    def unlock_user(self, person):
        super(ldap_datastore.PersonalDataStore, self).unlock_user(person)
        
        conn = LDAPClient()
        conn.unlock_user('uid=%s' % person.username)


class AccountDataStore(ldap_datastore.AccountDataStore):
    pass
