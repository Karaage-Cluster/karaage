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

    password_file = '/tmp/passwd'

    def create_account(self, person, default_project):
        ua = super(AccountDataStore, self).create_account(person, default_project)
        
        home_dir = '/home/%s' % person.username
        userid = self.get_next_uid()

        line = "%s:x:%s:%s:%s:%s:%s\n" % (person.username, userid, person.institute.gid, person.get_full_name(), home_dir, '/bin/bash')

        f = open(password_file, 'a')
        f.write(line)
        f.close()



    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)

        f = open(password_file)
        data = f.readlines()
        f.close()
        new_data = []
        for l in data:
            if l.find(ua.username) != 0:
                new_data.append(l)

        f = open(password_file, 'w')
        f.writelines(new_data)
        f.close()


    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)
        
        f = open(password_file)
        data = f.readlines()
        f.close()
        new_data = []
        for l in data:
            if l.find(ua.username) == 0:
                username, shad, uid, gid, name, homedir, shell = l.split(':')
                homedir = '/home/%s' % ua.username
                l = "%s:x:%s:%s:%s:%s:%s\n" % str(ua.username, uid, ua.user.institute.gid, ua.user.get_full_name(), homedir, shell)
                l = str(l)
            new_data.append(l)

        
        f = open(password_file, 'w')
        f.writelines(new_data)
        f.close()


    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)
        

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)

 
    def get_next_uid(self):
        f = open(password_file)
        data = f.readlines()
        f.close()
        id_list = []
        for l in data:
            id_list.append(int(l.split(':')[1]))

        id_list.sort()
        return id_list[-1] + 1


