from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

import datetime
from django_common.middleware.threadlocals import get_current_user

from karaage.util.helpers import create_password_hash 
from karaage.people.models import Person
from karaage.machines.models import UserAccount


class PersonalDataStore(object):


    def create_new_user(self, data, hashed_password=None):
        """Creates a new user (not active)

        Keyword arguments:
        data -- a dictonary of user data
        hashed_password -- 
    
        """
        random_passwd = User.objects.make_random_password()
        u = User.objects.create_user(data['username'], data['email'], random_passwd)
        
        if hashed_password:
            u.password = hashed_password
        else:
            u.password = create_password_hash(data['password1'])
            
        u.is_active = False
        u.save()
    
        #Create Person
        person = Person.objects.create(
            user=u, first_name=data['first_name'],
            last_name=data['last_name'],
            position=data['position'],department=data['department'],
            institute=data['institute'],
            title=data['title'], address=data['address'],
            country=data['country'],
            website=data['website'], fax=data['fax'],
            comment=data['comment'], telephone=data['telephone'],
            mobile=data['mobile'],
            )
        
        try:
            LogEntry.objects.create(
                action_time=datetime.datetime.now(), user=get_current_user(),
                content_type=ContentType.objects.get_for_model(person.__class__),
                object_id=person.id, object_repr=person.__str__(), action_flag=ADDITION,
                change_message='Created')
        except:
            pass
        
        return person


    def activate_user(self, person):
        """ Activates a user """
        approver = get_current_user().get_profile()
    
        person.date_approved = datetime.datetime.today()
        person.approved_by = approver
        person.deleted_by = None
        person.date_deleted = None
        person.user.is_active = True
        person.user.save()
        
        LogEntry.objects.create(
            action_time=datetime.datetime.now(), user=get_current_user(),
            content_type=ContentType.objects.get_for_model(person.__class__),
            object_id=person.id, object_repr=person.__str__(), action_flag=ADDITION,
            change_message='Activated')

        return person
        

    def delete_user(self, person):
        """ Sets Person not active and deletes all UserAccounts"""
        person.user.is_active = False
        person.expires = None
        person.user.save()
    
        deletor = get_current_user()
    
        person.date_deleted = datetime.datetime.today()
        person.deleted_by = deletor.get_profile()
        person.save()

        from karaage.datastores import delete_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            delete_account(ua)
            
        LogEntry.objects.create(
            action_time=datetime.datetime.now(), user=get_current_user(),
            content_type=ContentType.objects.get_for_model(person.__class__),
            object_id=person.id, object_repr=str(person), action_flag=DELETION,
            change_message='Deleted person')    



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
        person.user.set_password(raw_password)
        person.user.save()


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
            default_project.users.add(person)
    
        LogEntry.objects.create(
            action_time=datetime.datetime.now(), user=get_current_user(),
            content_type=ContentType.objects.get_for_model(ua.user.__class__),
            object_id=ua.user.id, object_repr=ua.user.__str__(), action_flag=ADDITION,
            change_message='Created account on %s' % self.machine_category)
            
        return ua



    def delete_account(self, ua):
        
        if not ua.date_deleted:
            ua.date_deleted = datetime.datetime.now()
            ua.save()

        for p in ua.project_list():
            p.users.remove(ua.user)
        
        
        LogEntry.objects.create(
            action_time=datetime.datetime.now(), user=get_current_user(),
            content_type=ContentType.objects.get_for_model(ua.user.__class__),
            object_id=ua.user.id, object_repr=ua.user.__str__(), action_flag=DELETION,
            change_message='Deleted account on %s' % ua.machine_category)
        


    def update_account(self, ua):
        pass

    def lock_account(self, ua):
        pass    

    def unlock_account(self, ua):
        pass
        
