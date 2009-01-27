from django.core.mail import mail_admins
from django.conf import settings

import base


class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password):
        return super(PersonalDataStore, self).create_new_user(data, hashed_password)

    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)
        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        

    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)


    def is_locked(self, person):
        super(PersonalDataStore, self).is_locked(person)


    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)
        

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        
        


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        ua = super(AccountDataStore, self).create_account(person, default_project)
        

        #line = "%s:x:%s:%s:%s:%s:%s" % (person.username, userid, person.institute.gid, person.get_full_name(), home_dir, '/bin/bash')

        #f = open('/etc/passwd')




    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)


    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
  

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)
        

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

 

