from django.contrib.auth.models import User
from django.conf import settings

from karaage.datastores import person_exists, account_exists
from karaage.validators import username_re
from karaage.machines.models import MachineCategory


class UsernameException(Exception):
    pass


class UsernameInvalid(UsernameException):
    pass


class UsernameTaken(UsernameException):
    pass
    
    
def validate_username(username):
    
        if username:
            if not username.islower():
                raise UsernameInvalid(u'Username must be all lowercase')
            if len(username) < 2:
                raise UsernameInvalid(u'Username must be at least 2 characters')
            if not username_re.search(username):
                raise UsernameInvalid(u'Usernames can only contain letters, numbers and underscores')

            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                user = None

            if user is not None:
                raise UsernameTaken(u'The username is already taken. Please choose another. If this was the name of your old account please email %s' % settings.ACCOUNTS_EMAIL)

            if person_exists(username):
                raise UsernameTaken(u'Username is already in external personal datastore.')

            for mc in MachineCategory.objects.all():
                if account_exists(username, mc):
                     raise UsernameTaken(u'Username is already in external account datastore.')

        return username
