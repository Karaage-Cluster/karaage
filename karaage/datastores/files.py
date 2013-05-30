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

from karaage.datastores import base


class PersonalDataStore(base.PersonalDataStore):
    
    def activate_user(self, person):
        super(PersonalDataStore, self).activate_user(person)

    def delete_user(self, person):
        super(PersonalDataStore, self).delete_user(person)
        
    def update_user(self, person):
        super(PersonalDataStore, self).update_user(person)

    def lock_user(self, person):
        super(PersonalDataStore, self).lock_user(person)

    def unlock_user(self, person):
        super(PersonalDataStore, self).unlock_user(person)
        

class AccountDataStore(base.AccountDataStore):
    
    passwd_files = settings.PASSWD_FILES

    def create_account(self, ua):
        super(AccountDataStore, self).create_account(ua)

        person = ua.user

        home_dir = '/home/%s' % ua.username
        userid = self.get_next_uid()

        line = "%s:x:%s:%s:%s:%s:%s\n" % (ua.username, userid, person.institute.gid, person.get_full_name(), home_dir, settings.DEFAULT_SHELL)

        for pwfile in self.passwd_files:
            f = open(pwfile, 'a')
            f.write(line)
            f.close()

    def delete_account(self, ua):
        super(AccountDataStore, self).delete_account(ua)

        for pwfile in self.passwd_files:

            f = open(pwfile)
            data = f.readlines()
            f.close()
            new_data = []
            for l in data:
                if l.find(ua.username) != 0:
                    new_data.append(l)

            f = open(file, 'w')
            f.writelines(new_data)
            f.close()

    def update_account(self, ua):
        super(AccountDataStore, self).update_account(ua)

        for pwfile in self.passwd_files:
            f = open(pwfile)
            data = f.readlines()
            f.close()
            new_data = []
            for l in data:
                if l.find(ua.username) == 0:
                    username, shad, uid, gid, name, homedir, shell = l.split(':')
                    homedir = '/home/%s' % ua.username
                    l = "%s:x:%s:%s:%s:%s:%s\n" % (ua.username, uid, ua.user.institute.gid, ua.user.get_full_name(), homedir, shell)
                new_data.append(l)

            f = open(pwfile, 'w')
            f.writelines(new_data)
            f.close()

    def lock_account(self, ua):
        super(AccountDataStore, self).lock_account(ua)

    def unlock_account(self, ua):
        super(AccountDataStore, self).unlock_account(ua)
 
    def get_next_uid(self):
        id_list = []

        for pwfile in self.passwd_files:
            f = open(pwfile)
            data = f.readlines()
            f.close()
            for l in data:
                try:
                    id_list.append(int(l.split(':')[2]))
                except:
                    pass

        id_list.sort()
        id = id_list[-1] + 1

        if id < settings.UID_START:
            return settings.UID_START
        else:
            return id
