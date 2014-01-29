.. index:: pair: data store;openldap
Adding OpenLDAP
===============

OpenLDAP installation
---------------------

1. Run the following commands:

   .. code-block:: bash

      apt-get install slapd
      apt-get install ldap-utils
      ldapadd -Y EXTERNAL -H ldapi:///  < /etc/ldap/schema/ppolicy.ldif

2. Create the file with the following contents in /tmp/ppolicy.ldif (note: replace dc=example,dc=org with your base DN)::

      dn: ou=People,dc=example,dc=org
      objectClass: organizationalUnit

      dn: ou=Groups,dc=example,dc=org
      objectClass: organizationalUnit

      dn: ou=policies,dc=example,dc=org
      objectClass: organizationalUnit

      dn: cn=default,ou=policies,dc=example,dc=org
      objectClass: top
      objectClass: device
      objectClass: pwdPolicy
      pwdAttribute: 2.5.4.35

3. Import with the following command:

   .. code-block:: bash

      ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy.ldif

4. Create the file with the following contents in /tmp/ppolicy.ldif::

      dn: cn=module,cn=config
      objectClass: olcModuleList
      cn: module
      olcModulepath: /usr/lib/ldap
      olcModuleload: ppolicy.so

      dn: olcOverlay=ppolicy,olcDatabase={1}hdb,cn=config
      objectClass: olcPPolicyConfig
      olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

5. Import with the following command:

   .. code-block:: bash

      ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy.ldif

.. todo::

   REPLICATION

   CENTOS

   See http://itdavid.blogspot.com.au/2012/06/howto-openldap-24-replication-on-centos.html


Configuring Karaage to use LDAP
-------------------------------
1. Add the following to /etc/karaage/global_settings.py:

   .. code-block:: python


      LDAP = {
          'default': {
              'ENGINE': 'tldap.backend.fake_transactions',
              'URI': 'ldap://localhost',
              'USER': 'cn=admin,dc=example,dc=org',
              'PASSWORD': 'XXXXXXXX',
              'USE_TLS': False,
              'TLS_CA' : None,
              'LDAP_ACCOUNT_BASE': 'ou=People,dc=example,dc=org',
              'LDAP_GROUP_BASE': 'ou=Groups,dc=example,dc=org',
          }
      }

      DATASTORES = {
          'ldap' : [
              {
                  'DESCRIPTION': 'Default LDAP datastore',
                  'ENGINE': 'karaage.datastores.ldap.AccountDataStore',
                  'LDAP': 'default',
                  'ACCOUNT': 'karaage.datastores.ldap_schemas.openldap_account',
                  'GROUP': 'karaage.datastores.ldap_schemas.openldap_group',
                  'PRIMARY_GROUP': "institute",
                  'DEFAULT_PRIMARY_GROUP': "dummy",
                  'HOME_DIRECTORY': "/home/%(uid)s",
                  'LOCKED_SHELL': "/usr/local/sbin/locked",
              },
          ],
          'dummy' : [
          ],
      }


2. Reload apache.

   .. code-block:: bash

      service apache2 reload
      service karaage3-celery restart

3. Log into web interface and add a machine category that references the ldap
   datastore. This should automatically populate LDAP with any entries you have
   created.
