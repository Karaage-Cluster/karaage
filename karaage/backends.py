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

from karaage.datastores import ldap_schemas


class LDAPBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            ldap_user = ldap_schemas.person.objects.get(pk=username)
        except ldap_schemas.person.AccountDoesNotExist:
            return None

        if ldap_user.check_password(password):

            # The user existed and authenticated. Get the user
            # record or create one with no privileges.
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                # Theoretical backdoor could be input right here. We don't
                # want that, so input an unused random password here.
                # The reason this is a backdoor is because we create a
                # User object for LDAP users so we can get permissions,
                # however we -don't- want them able to login without
                # going through LDAP with this user. So we effectively
                # disable their non-LDAP login ability by setting it to a
                # random password that is not given to them. In this way,
                # static users that don't go through ldap can still login
                # properly, and LDAP users still have a User object.
                user = User.objects.create_user(username, '')
                user.set_unusable_password()
                user.is_staff = False
                user.save()
            # Success.
            return user

        else:
            return None
