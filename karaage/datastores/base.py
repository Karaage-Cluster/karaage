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

from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

import datetime
from andsome.middleware.threadlocals import get_current_user

from karaage.people.models import Person
from karaage.machines.models import UserAccount
from karaage.util import log_object as log

class PersonalDataStore(object):


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
            from karaage.datastores import create_password_hash
            user.password = create_password_hash(data['password1'])
            
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
            is_systemuser=data.get('is_systemuser', ''),
            saml_id=data.get('saml_id', ''),
            )
        
        try:
            current_user = get_current_user()
            if current_user.is_anonymous():
                current_user = person.user
        except:
            current_user = person.user

        log(current_user, person, 1, 'Created')
        
        return person

    def create_new_person_from_applicant(self, applicant):
        from karaage.datastores import create_new_user
        data = {
            'email': applicant.email,
            'username': applicant.username,
            'title': applicant.title,
            'first_name': applicant.first_name,
            'last_name': applicant.last_name,
            'institute': applicant.institute,
            'department': applicant.department,
            'position': applicant.position,
            'telephone':applicant.telephone,
            'mobile': applicant.mobile,
            'supervisor': applicant.supervisor,
            'address': applicant.address,
            'city': applicant.city,
            'postcode': applicant.postcode,
            'country': applicant.country,
            'fax':  applicant.fax,
            'saml_id': applicant.saml_id,
            }
        
        return create_new_user(data, hashed_password=applicant.password)


    def activate_user(self, person):
        """ Activates a user """
        try:
            current_user = get_current_user()
            if current_user.is_anonymous():
                current_user = person.user
        except:
            current_user = person.user

        person.date_approved = datetime.datetime.today()

        person.approved_by = current_user.get_profile()
        person.deleted_by = None
        person.date_deleted = None
        person.user.is_active = True
        person.user.save()

        log(current_user, person, 1, 'Activated')

        return person
        

    def delete_user(self, person):
        """ Sets Person not active and deletes all UserAccounts"""
        person.user.is_active = False
        person.expires = None
        person.user.save()
    
        deletor = get_current_user()
    
        person.date_deleted = datetime.datetime.today()
        person.deleted_by = deletor.get_profile()
        person.save(update_datastore=False)

        from karaage.datastores import delete_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            delete_account(ua)

        log(deletor, person, 3, 'Deleted')    


    def update_user(self, person):
        from karaage.datastores import update_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            update_account(ua)
        
    def is_locked(self, person):
        pass

    def lock_user(self, person):
        from karaage.datastores import lock_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            lock_account(ua)


    def unlock_user(self, person):
        from karaage.datastores import unlock_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            unlock_account(ua)


    def set_password(self, person, raw_password):
        pass

    def user_exists(self, username):
        pass

    def create_password_hash(self, raw_password):
        pass


class AccountDataStore(object):

    def __init__(self, machine_category):
        self.machine_category = machine_category
    
    def create_account(self, person, default_project):
        """Creates a UserAccount (if needed) and activates user.

        Keyword arguments:
        person_id -- Person id
        project_id -- Project id
        
        """   
        ua = UserAccount.objects.create(
            user=person, username=person.username,
            machine_category=self.machine_category,
            default_project=default_project,
            date_created=datetime.datetime.today())
    
        if default_project is not None:
            from karaage.projects.utils import add_user_to_project
            add_user_to_project(person, default_project)
    
        log(get_current_user(), ua.user, 1, 'Created account on %s' % self.machine_category)

        return ua


    def delete_account(self, ua):       
        if not ua.date_deleted:
            ua.date_deleted = datetime.datetime.now()
            ua.save()
        for project in ua.project_list():
            project.users.remove(ua.user)
            project.save()
        log(get_current_user(), ua.user, 3, 'Deleted account on %s' % ua.machine_category)
        
    def update_account(self, ua):
        pass

    def lock_account(self, ua):
        ua.previous_shell = ua.loginShell()
        ua.save()
        from karaage.datastores import change_shell
        change_shell(ua, settings.LOCKED_SHELL)

    def unlock_account(self, ua):
        shell = getattr(ua, 'previous_shell', '/bin/bash')
        from karaage.datastores import change_shell
        change_shell(ua, shell)

    def get_shell(self, ua):
        pass

    def change_shell(self, ua, shell):
        from karaage.datastores import get_shell
        ua.previous_shell = get_shell(ua)
        ua.save()

