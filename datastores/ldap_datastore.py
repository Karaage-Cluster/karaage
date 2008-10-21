from placard.connection import LDAPConnection

import base


class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password=None):
        super(LDAPPersonalDataStore, self).create_new_user(data, hashed_password=None)

    def activate_user(self, person):
        super(LDAPPersonalDataStore, self).activate_user(person)

        attrs = {}
        attrs['uid'] = str(person.username)
        attrs['givenName'] = str(person.first_name)
        attrs['sn'] = str(person.last_name)
        attrs['telephoneNumber'] = str(person.telephone)
        attrs['mail'] = str(person.email)
        attrs['o'] = str(person.institute.name)
        attrs['userPassword'] = str(person.user.password)
        
        conn = LDAPConnection()
        conn.add_user(**attrs)
        

    def delete_user(self, person):
        super(LDAPPersonalDataStore, self).delete_user(person)

        conn = LDAPConnection()
        conn.delete_user(person.user.username)
        

class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        super(LDAPAccountDataStore, self).create_account(person, default_project)
            
        conn = LDAPConnection()
        
        #TODO - Get generated attrs from ldap_attrs.py
        conn.update_user(
            person.username,
            gecos='%s %s (%s)' % (str(person.first_name), str(person.last_name), str(person.institute.name)),
            uidNumber=conn.get_new_uid(),
            gidNumber=str(person.institute.gid),
            homeDirectory='/home/%s' % str(person.username),
            loginShell='/bin/bash',
            objectClass=['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount','posixAccount']
            )


    def delete_account(self, ua):
        super(LDAPAccountDataStore, self).delete_account(ua)

        conn = LDAPConnection()

        #TODO - Get generated attrs from ldap_attrs.py

        conn.update_user(
            ua.username,
            gecos='', 
            uidNumber='',
            gidNumber='',
            homeDirectory='',
            loginShell='',
            objectClass=['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount',]
            )
