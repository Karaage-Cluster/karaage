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

    def is_locked(self, person):
        super(PersonalDataStore, self).is_locked(person)

    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)

    def set_password(self, person, raw_password):
        super(PersonalDataStore, self).set_password(person, raw_password)


class AccountDataStore(base.AccountDataStore):

    def create_account(self, person, default_project):
        return super(AccountDataStore, self).create_account(person, default_project)

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
  
    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)
