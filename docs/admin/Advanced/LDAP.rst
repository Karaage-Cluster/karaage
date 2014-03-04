Advanced LDAP handling
======================

To modify how Karaage interfaces with LDAP you will need to modify your
ldap\_attrs.py file in /etc/karaage

Anything in this file will override anything in the default
ldap\_attrs.py file.

The default ldap\_attrs.py file is located at
/karaage/conf/ldap\_attrs.py

See
https://code.vpac.org/hudson/job/django-placard/javadoc/ref/ldap\_attrs\_settings.html
for full instructions on ldap\_attrs.

Examples
--------

Changing the primary group of a newly created user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example: Create a new group with the same name as the users username

::

    # File: /etc/karaage/ldap_attrs.py
    # Define method to create a group with the same name as user
    def get_create_own_gid(data):
        # Only assign a GID if the user has a POSIX account
        if 'posixAccount' in data['objectClass']:
            from placard.client import LDAPClient
            from placard.exceptions import DoesNotExistException
            conn = LDAPClient()
            try:
                group = conn.get_group('cn=%s' % data['uid'])
                gid = group.gidNumber
            except DoesNotExistException:
                gid = conn.add_group(cn=data['uid'])

            return gid
        return ''


    # Override the default behaviour
    GENERATED_USER_ATTRS['gidNumber'] = get_create_own_gid

