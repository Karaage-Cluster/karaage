from django.contrib.auth.backends import ModelBackend

from karaage.people.models import Person

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from karaage.people.models import Person
import tldap.methods.ldap_passwd


class LDAPBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            person = Person.objects.get(user__username__exact=username)
        except Person.DoesNotExist:
            return None

        if person.legacy_ldap_password is None:
            return None

        up = tldap.methods.ldap_passwd.UserPassword()
        if not up._compareSinglePassword(password, person.legacy_ldap_password):
            return None

        # Success.
        person.user.set_password(password)
        person.user.save()
        person.legacy_ldap_password = None
        person.save()

        return person.user
