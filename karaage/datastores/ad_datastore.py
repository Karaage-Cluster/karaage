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
from django.contrib.auth.models import User

from placard.client import LDAPClient
from placard.exceptions import DoesNotExistException

from karaage.people.models import Person
from karaage.datastores import base
from karaage.util import log_object as log

class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password=None):
        """Creates a new user (not active)
        Keyword arguments:
        data -- a dictonary of user data
        hashed_password --
        """
        # Make sure username isn't taken in Datastore
        random_passwd = User.objects.make_random_password()
        user = User.objects.create_user(data['username'], data['email'], random_passwd)
        
        if hashed_password:
            user.password = hashed_password
        else:
            user.password = unicode("\"" + str(data['password1']) + "\"", "iso-8859-1").encode("utf-16-le")
       
        user.is_active = False
        user.save()
       
        #Create Person 
        person = Person.objects.create(
            user=user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            institute=data['institute'],
            position=data.get('position', ''),
            department=data.get('department', ''),
            title=data.get('title', ''),
            address=data.get('address', ''),
            country=data.get('country', ''),
            website=data.get('website', ''),
            fax=data.get('fax', ''),
            comment=data.get('comment', ''),
            telephone=data.get('telephone', ''),
            mobile=data.get('mobile', ''),
            supervisor=data.get('supervisor', ''),
            )
      
        try:
            current_user = get_current_user()
            if current_user.is_anonymous():
                current_user = person.user
        except:
            current_user = person.user
         
        log(current_user, person, 1, 'Created')

        return person
  
     
    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)
        attrs = {}
        attrs['sAMAccountName'] = str(person.username)
        attrs['givenName'] = str(person.first_name)
        attrs['sn'] = str(person.last_name)
        attrs['telephoneNumber'] = str(person.telephone)
        attrs['mail'] = str(person.email)
        attrs['o'] = str(person.institute.name)
        conn = LDAPClient()
        dn = conn.add_user(**attrs)
        person.save(update_datastore=False)
        
        # Set password then unlock account
        if person.user.password != '!':
            import ldap
            mod_attrs = [( ldap.MOD_REPLACE, 'unicodePwd', person.user.password),( ldap.MOD_REPLACE, 'unicodePwd', person.user.password)]
            conn.conn.modify_s(dn, mod_attrs)
            conn.update_user('sAMAccountName=%s' % str(person.username), userAccountControl=512)
            
        person.user.set_unusable_password()
        person.user.save()
        del(conn)
        return person
   
    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        conn = LDAPClient()
        conn.delete_user('uid=%s' % person.user.username)

    def update_user(self, person):
        conn = LDAPClient()
        
        conn.update_user(
            'sAMAccountName=%s' % person.username,
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
            ldap_user = conn.get_user('sAMAccountName=%s' % person.username)
        except DoesNotExistException:
            return True
        if ldap_user.userAccountControl != '512':
            return True
      
        return False
   
    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)
        
        conn = LDAPClient()
        conn.update_user(
            'sAMAccountName=%s' % person.username,
            userAccountControl=514,
            )
      
    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        
        conn = LDAPClient()
        conn.update_user(
            'sAMAccountName=%s' % person.username,
            userAccountControl=512,
            )

    def set_password(self, person, raw_password):
        conn = LDAPClient()
        conn.change_password('sAMAccountName=%s' % person.user.username, raw_password)

class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        ua = super(AccountDataStore, self).create_account(person, default_project)          
        conn = LDAPClient()
      
        ldap_attrs = __import__(settings.LDAP_ATTRS, {}, {}, [''])
      
        data = conn.get_user('sAMAccountName=%s' % person.username).__dict__
        
        data['cluster_account'] = True
        data['objectClass'] = settings.ACCOUNT_OBJECTCLASS
        data['default_project'] = default_project
        data['person'] = person
        conn.update_user(
            'sAMAccountName=%s' % person.username,
            objectClass=settings.ACCOUNT_OBJECTCLASS,
            uidNumber=ldap_attrs.GENERATED_USER_ATTRS['uidNumber'](data),
            gidNumber=ldap_attrs.GENERATED_USER_ATTRS['gidNumber'](data),
            unixHomeDirectory=ldap_attrs.GENERATED_USER_ATTRS['unixHomeDirectory'](data),
            loginShell=ldap_attrs.GENERATED_USER_ATTRS['loginShell'](data),
            uid=person.username,
            msSFU30Name=person.username,
            msSFU30NisDomain=settings.LDAP_NISDOMAIN,
            unixUserPassword='ABCD!efgh12345$67890',
            )
        del(conn)
        return ua

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)
        conn = LDAPClient()
        
        conn.update_user(
            'sAMAccountName=%s' % ua.username,
            uidNumber='',
            gidNumber='',
            unixHomeDirectory='',
            loginShell='',
            msSFU30Name='',
            msSFU30NisDomain='',
            unixUserPassword='',
            objectClass=settings.USER_OBJECTCLASS
            )
      
    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
        conn = LDAPClient()
        ldap_attrs = __import__(settings.LDAP_ATTRS, {}, {}, [''])
        
        data = conn.get_user('sAMAccountName=%s' % ua.username).__dict__
        data['default_project'] = ua.default_project
        data['person'] = ua.user
        
        conn.update_user(
            'sAMAccountName=%s' % ua.username,
            unixHomeDirectory=ldap_attrs.GENERATED_USER_ATTRS['unixHomeDirectory'](data),
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
        luser = conn.get_user('sAMAccountName=%s' % ua.username)
        return luser.loginShell

    def change_shell(self, ua, shell):
        super(AccountDataStore, self).change_shell(ua, shell)
        conn =  LDAPClient()
        conn.update_user('sAMAccountName=%s' % ua.username, loginShell=str(shell))
