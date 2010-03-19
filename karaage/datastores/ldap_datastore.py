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

from django.core.mail import mail_admins
from django.conf import settings

from placard.client import LDAPClient
from placard.exceptions import DoesNotExistException

import base


class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password):
        return super(PersonalDataStore, self).create_new_user(data, hashed_password)

    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)

        attrs = {}
        attrs['uid'] = str(person.username)
        attrs['givenName'] = str(person.first_name)
        attrs['sn'] = str(person.last_name)
        attrs['telephoneNumber'] = str(person.telephone)
        attrs['mail'] = str(person.email)
        attrs['o'] = str(person.institute.name)
        attrs['userPassword'] = str(person.user.password)
        
        conn = LDAPClient()
        conn.add_user(**attrs)
        person.save(update_datastore=False)

        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)

        conn = LDAPClient()
        conn.delete_user('uid=%s' % person.user.username)
        

    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)

        conn = LDAPClient()
    
        conn.update_user(
            'uid=%s' % person.username,
            cn='%s %s' % (str(person.first_name), str(person.last_name)),
            givenName=str(person.first_name),
            sn=str(person.last_name),
            telephoneNumber=str(person.telephone),
            mail=str(person.email),
            o=str(person.institute.name),
            )

    def is_locked(self, person):
        super(PersonalDataStore, self).is_locked(person)

        conn = LDAPClient()
        try:
            ldap_user = conn.get_user('uid=%s' % person.username)
        except DoesNotExistException:
            return True

        if hasattr(ldap_user, 'nsAccountLock'):
            return True

        return False


    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)
        
        conn = LDAPClient()
        conn.update_user(
            'uid=%s' % person.username,
            nsRoleDN='cn=nsManagedDisabledRole,dc=vpac,dc=org',
            )
        

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        
        conn = LDAPClient()
        dn="uid=%s,%s" % (person.username, settings.LDAP_USER_BASE)
        old = {
            'nsRoleDN': 'cn=nsManagedDisabledRole,dc=vpac,dc=org',
            }
        new = {}
        conn.ldap_modify(dn, old, new)
    

    def set_password(self, person, raw_password):
        conn = LDAPClient()
        conn.change_password('uid=%s' % person.user.username, raw_password)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        ua = super(AccountDataStore, self).create_account(person, default_project)
            
        conn = LDAPClient()
        
        #TODO - Get generated attrs from ldap_attrs.py
        conn.update_user(
            'uid=%s' % person.username,
            gecos='%s %s (%s)' % (str(person.first_name), str(person.last_name), str(person.institute.name)),
            uidNumber=conn.get_new_uid(),
            gidNumber=str(person.institute.gid),
            homeDirectory='/home/%s' % str(person.username),
            loginShell='/bin/bash',
            objectClass=['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount','posixAccount']
            )

        return ua


    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)

        conn = LDAPClient()

        #TODO - Get generated attrs from ldap_attrs.py

        conn.update_user(
            'uid=%s' % ua.username,
            gecos='', 
            uidNumber='',
            gidNumber='',
            homeDirectory='',
            loginShell='',
            objectClass=['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount',]
            )


    def update_account(self, ua):

        super(AccountDataStore, self).update_account(ua)

        conn = LDAPClient()

        conn.update_user(
            'uid=%s' % ua.user.username,
            gecos='%s %s (%s)' % ((ua.user.first_name), str(ua.user.last_name), str(ua.user.institute.name)),
            gidNumber=str(ua.user.institute.gid),
            )


    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

        conn = LDAPClient()
        
        conn.update_user(
            'uid=%s' % ua.username,
            loginShell='/usr/local/sbin/insecure'
            )
        

    def unlock_account(self, ua):
        shell = super(AccountDataStore, self).unlock_account(ua)

        conn = LDAPClient()
        conn.update_user('uid=%s' % ua.username, loginShell=shell)
        

    def get_shell(self, ua):
        super(AccountDataStore, self).get_shell(ua)

        conn = LDAPClient()
        luser = conn.get_user('uid=%s' % ua.username)
        return luser.loginShell


    def change_shell(self, ua, shell):
        super(AccountDataStore, self).change_shell(ua, shell)

        conn =  LDAPClient()
        conn.update_user('uid=%s' % ua.username, loginShell=str(shell))
