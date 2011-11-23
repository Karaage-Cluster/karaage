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

from django.conf import settings

from placard.client import LDAPClient
from placard.exceptions import DoesNotExistException

from karaage.datastores import base


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
        person.user.set_unusable_password()
        person.user.save()
        person.save(update_datastore=False)
        del(conn)
        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)

        conn = LDAPClient()
        try:
            conn.delete_user('uid=%s' % person.user.username)
        except DoesNotExistException:
            pass

    def update_user(self, person):
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
        del(conn)
        super(PersonalDataStore, self).update_user(person)

    def is_locked(self, person):
        super(PersonalDataStore, self).is_locked(person)

        conn = LDAPClient()
        try:
            ldap_user = conn.get_user('uid=%s' % person.username)
        except DoesNotExistException:
            return True
        output = conn.ldap_search(settings.LDAP_USER_BASE,
                                  'uid=%s' % person.username,
                                  retrieve_attributes=['nsAccountLock'])
        if output[0][1]:
            return True
        
        return False

    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)
        
        conn = LDAPClient()
        conn.update_user(
            'uid=%s' % person.username,
            nsRoleDN=settings.LDAP_LOCK_DN,
            )
        del(conn)
        
    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        
        conn = LDAPClient()
        dn = "uid=%s,%s" % (person.username, settings.LDAP_USER_BASE)
        old = {
            'nsRoleDN': settings.LDAP_LOCK_DN,
            }
        new = {}
        conn.ldap_modify(dn, old, new)
        del(conn)

    def set_password(self, person, raw_password):
        conn = LDAPClient()
        conn.change_password('uid=%s' % person.user.username, raw_password)
        del(conn)

    def user_exists(self, username):
        conn = LDAPClient()
        try:
            conn.get_user('uid=%s' % username)
            return True
        except DoesNotExistException:
            return False
        
    def create_password_hash(self, raw_password):
        from placard.ldap_passwd import md5crypt
        return '{crypt}%s' % md5crypt(raw_password)

    def change_username(self, person, new_username):
        conn = LDAPClient()
        conn.change_uid('uid=%s' % person.user.username, new_username)
        del(conn)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        ua = super(AccountDataStore, self).create_account(person, default_project)
        conn = LDAPClient()
        
        ldap_attrs = __import__(settings.LDAP_ATTRS, {}, {}, [''])
        
        data = conn.get_user('uid=%s' % person.username).__dict__
        data['objectClass'] = settings.ACCOUNT_OBJECTCLASS
        data['default_project'] = default_project
        data['person'] = person
        conn.update_user(
            'uid=%s' % person.username,
            gecos=ldap_attrs.GENERATED_USER_ATTRS['gecos'](data),
            uidNumber=ldap_attrs.GENERATED_USER_ATTRS['uidNumber'](data),
            gidNumber=ldap_attrs.GENERATED_USER_ATTRS['gidNumber'](data),
            homeDirectory=ldap_attrs.GENERATED_USER_ATTRS['homeDirectory'](data),
            loginShell=ldap_attrs.GENERATED_USER_ATTRS['loginShell'](data),
            objectClass=settings.ACCOUNT_OBJECTCLASS
            )
        del(conn)
        return ua

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)
        conn = LDAPClient()

        conn.update_user(
            'uid=%s' % ua.username,
            gecos='',
            uidNumber='',
            gidNumber='',
            homeDirectory='',
            loginShell='',
            objectClass=settings.USER_OBJECTCLASS
            )
        del(conn)

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
        conn = LDAPClient()
        ldap_attrs = __import__(settings.LDAP_ATTRS, {}, {}, [''])
        
        data = conn.get_user('uid=%s' % ua.username).__dict__
        data['default_project'] = ua.default_project
        data['person'] = ua.user

        conn.update_user(
            'uid=%s' % ua.username,
            homeDirectory=ldap_attrs.GENERATED_USER_ATTRS['homeDirectory'](data),
            gecos=ldap_attrs.GENERATED_USER_ATTRS['gecos'](data),
            gidNumber=ldap_attrs.GENERATED_USER_ATTRS['gidNumber'](data),
            )
        del(conn)

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

    def get_shell(self, ua):
        super(AccountDataStore, self).get_shell(ua)
        conn = LDAPClient()
        luser = conn.get_user('uid=%s' % ua.username)
        return luser.loginShell

    def change_shell(self, ua, shell):
        super(AccountDataStore, self).change_shell(ua, shell)
        conn = LDAPClient()
        conn.update_user('uid=%s' % ua.username, loginShell=str(shell))
        del(conn)
