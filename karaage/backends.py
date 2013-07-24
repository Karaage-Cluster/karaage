from django.contrib.auth.backends import ModelBackend

from karaage.people.models import Person


class SamlUserBackend(ModelBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    def authenticate(self, saml_user):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not saml_user:
            return
        user = None
        username = self.clean_username(saml_user)

        try:
            user = Person.objects.get(saml_id=username).user
        except Person.DoesNotExist:
            pass
        return user

    def clean_username(self, username):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        return username

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        return user


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
