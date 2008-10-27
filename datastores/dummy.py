from placard.connection import LDAPConnection

import base


class PersonalDataStore(base.PersonalDataStore):
    
    def create_new_user(self, data, hashed_password=None):
        return super(PersonalDataStore, self).create_new_user(data, hashed_password=None)

    def activate_user(self, person):
        person = super(PersonalDataStore, self).activate_user(person)
        person.save()
        return person

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        

    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        return super(AccountDataStore, self).create_account(person, default_project)



    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)


    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
