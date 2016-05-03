.. index:: pair: data store;openldap

Adding OpenLDAP
===============

Assumptions
-----------
You will need to substitute correct values for the following when applicable:

*  Base DN: ``dc=example,dc=org``
*  Administrator DN: ``cn=admin,dc=example,dc=org``
*  Administrator password: ``XXXXXXXX`` (do not use ``XXXXXXXX``).

..  todo::

    Need index to sections, otherwise reader may not notice that Debian is
    also documented.

    Need to document 389 configuration.

    RHEL 6 and Debian installations of OpenLDAP should be very similar, maybe
    these can be combined? Main difference is that RHEL 6 autoconfigures
    the database with stupid defaults, possible we should delete existing
    config and start with new clean configuration rather then patch the
    existing setup.

    RHEL6 openldap needs to be able to read certificate files. With Debian
    this is controlled by ssl-cert group.

RHEL 6 installation
-------------------
#.  Run the following commands:

    .. code-block:: bash

        yum install openldap-servers
        yum install openldap-clients
        cp -rv /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG
        chown -R ldap:ldap /var/lib/ldap
        cd /etc/openldap/slapd.d/cn=config

    Do not start the server yet.

#.  Encrypt the admin password:

    .. code-block:: bash

        slappasswd

    Enter ``XXXXXXXX`` twice. This should output an encrypted password starting
    with ``XXXXXXXX``. Copy that into the clipboard.

    The result for ``XXXXXXXX`` is ``{SSHA}4bxi0+aXeYvv2TGT10VWUIwcaynqBbxH``
    (do not use this value).

#.  Edit ``olcDatabase={2}bdb.ldif``, and update/add the following values. Do
    not change anything else::

        olcSuffix: dc=example,dc=org
        olcRootDN: cn=admin,dc=example,dc=org
        olcRootPW: {SSHA}4bxi0+aXeYvv2TGT10VWUIwcaynqBbxH

#.  Edit ``olcDatabase={1}monitor.ldif``, and update update the admin DN. Do
    not change anything else::

        olcAccess: {0}to *  by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=externa
         l,cn=auth" read  by dn.base="cn=admin,dc=example,dc=org" read  by * none

#.  Run the following commands:

    .. code-block:: bash

        service slapd start
        chkconfig slapd on

#.  Create the file with the following contents in ``/tmp/ldapssl.ldif``::

        dn: cn=config
        changetype: modify
        replace: olcTLSCertificateFile
        olcTLSCertificateFile: /etc/ssl/private/www_cert.pem
        -
        replace: olcTLSCertificatekeyFile
        olcTLSCertificatekeyFile: /etc/ssl/private/www_privatekey.pem
        -
        replace: olcTLSCACertificateFile
        olcTLSCACertificateFile: /etc/ssl/private/www_intermediate.pem

        dn: olcDatabase={2}bdb,cn=config
        changetype: modify
        delete: olcTLSCertificateFile
        -
        delete: olcTLSCertificateKeyFile

#.  Import with the following command:

    .. code-block:: bash

        ldapmodify -Y EXTERNAL -H ldapi:///  < /tmp/ldapssl.ldif

#.  Edit ``/etc/sysconfig/ldap``::

        SLAPD_LDAPS=yes

#.  Restart LDAP server.

    .. code-block:: bash

        service slapd restart

#.  Create the file with the following contents in ``/tmp/ppolicy1.ldif``::

        dn: cn=module,cn=config
        objectClass: olcModuleList
        cn: module
        olcModulepath: /usr/lib/ldap
        olcModuleload: ppolicy.so

        dn: olcOverlay=ppolicy,olcDatabase={1}hdb,cn=config
        objectClass: olcPPolicyConfig
        olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

        dn: olcDatabase={2}bdb,cn=config
        changetype: modify
        add: olcAccess
        olcAccess: to attrs=userPassword,shadowLastChange by anonymous auth by dn="cn=admin,dc=example,dc=org" write by * none
        olcAccess: to * by dn="cn=admin,dc=example,dc=org" write by * read

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy1.ldif

#.  Create the file with the following contents in ``/tmp/ppolicy2.ldif``::

        dn: dc=example,dc=org
        objectClass: top
        objectClass: domain

        dn: ou=Accounts,dc=example,dc=org
        objectClass: organizationalUnit

        dn: ou=Groups,dc=example,dc=org
        objectClass: organizationalUnit

        dn: ou=policies,dc=example,dc=org
        objectClass: organizationalUnit

        dn: cn=default,ou=policies,dc=example,dc=org
        objectClass: top
        objectClass: device
        objectClass: pwdPolicy
        pwdAttribute: userPassword

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy2.ldif

#.  Test ldap connections.

    .. code-block:: bash

        ldapsearch  -x -b'dc=example,dc=org' -D cn=admin,dc=example,dc=org -W -ZZ

    Fix any errors.

#.  Force the use of SSL for accessing the main database without disabling
    access to cn=config.  Create the file with the following contents in
    ``/tmp/security.ldif``::

        dn: olcDatabase={2}bdb,cn=config
        changetype: modify
        replace: olcSecurity
        olcSecurity: tls=1

#.  Import with the following command:

    .. code-block:: bash

        ldapmodify -Y EXTERNAL -H ldapi:/// < /tmp/security.ldif

    .. note::

        This won't guarantee that LDAP passwords are never sent in the
        clear, however such attempts should fail.

.. todo::

    REPLICATION

    See http://itdavid.blogspot.com.au/2012/06/howto-openldap-24-replication-on-centos.html


Debian installation
-------------------

#.  Run the following commands:

    .. code-block:: bash

        apt-get install slapd
        apt-get install ldap-utils
        addgroup openldap ssl-cert

    Enter ``XXXXXXXX`` when prompted for administrator’s password.

#.  Create the file with the following contents in ``/tmp/ppolicy1.ldif``::

        dn: cn=module,cn=config
        objectClass: olcModuleList
        cn: module
        olcModulepath: /usr/lib/ldap/
        olcModuleload: ppolicy.la

        dn: olcOverlay=ppolicy,olcDatabase={1}hdb,cn=config
        objectClass: olcPPolicyConfig
        olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

#.  Create the file with the following contents in ``/tmp/ldapssl.ldif``::

        dn: cn=config
        changetype: modify
        replace: olcTLSCertificateFile
        olcTLSCertificateFile: /etc/ssl/private/www_cert.pem
        -
        replace: olcTLSCertificatekeyFile
        olcTLSCertificatekeyFile: /etc/ssl/private/www_privatekey.pem
        -
        replace: olcTLSCACertificateFile
        olcTLSCACertificateFile: /etc/ssl/private/www_intermediate.pem

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -Y EXTERNAL -H ldapi:/// < /etc/ldap/schema/ppolicy.ldif
        ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy1.ldif
        ldapmodify -Y EXTERNAL -H ldapi:///  < /tmp/ldapssl.ldif

#.  Create the file with the following contents in ``/tmp/ppolicy2.ldif``::

        dn: ou=policies,dc=example,dc=org
        objectClass: organizationalUnit

        dn: ou=Accounts,dc=example,dc=org
        objectClass: organizationalUnit

        dn: ou=Groups,dc=example,dc=org
        objectClass: organizationalUnit

        dn: cn=default,ou=policies,dc=example,dc=org
        objectClass: top
        objectClass: device
        objectClass: pwdPolicy
        pwdAttribute: userPassword

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy2.ldif

#.  Test ldap connections.

    .. code-block:: bash

        ldapsearch  -x -b'dc=example,dc=org' -ZZ

    Fix any errors.

#.  Force the use of SSL for accessing the main database without disabling
    access to cn=config.  Create the file with the following contents in
    ``/tmp/security.ldif``::

        dn: olcDatabase={1}hdb,cn=config
        changetype: modify
        replace: olcSecurity
        olcSecurity: tls=1

#.  Import with the following command:

    .. code-block:: bash

        ldapmodify -Y EXTERNAL -H ldapi:/// < /tmp/security.ldif

    .. note::

        This won't guarantee that LDAP passwords are never sent in the
        clear, however such attempts should fail.

.. todo::

    REPLICATION


Configuring Karaage to use LDAP
-------------------------------
#.  Add the :setting:`LDAP` and :setting:`MACHINE_CATEGORY_DATASTORES` settings
    to ``/etc/karaage3/settings.py``:

    .. code-block:: python


        LDAP = {
             'default': {
                  'ENGINE': 'tldap.backend.fake_transactions',
                  'URI': 'ldap://www.example.org',
                  'USER': 'cn=admin,dc=example,dc=org',
                  'PASSWORD': 'XXXXXXXX',
                  'REQUIRE_TLS': True,
                  'START_TLS': True,
                  'TLS_CA': None,
             }
        }

        MACHINE_CATEGORY_DATASTORES = {
             'ldap': [
                  {
                        'DESCRIPTION': 'LDAP datastore',
                        'ENGINE': 'karaage.datastores.ldap.MachineCategoryDataStore',
                        'LDAP': 'default',
                        'ACCOUNT': 'karaage.datastores.ldap_schemas.openldap_account',
                        'GROUP': 'karaage.datastores.ldap_schemas.openldap_account_group',
                        'PRIMARY_GROUP': "institute",
                        'DEFAULT_PRIMARY_GROUP': "dummy",
                        'HOME_DIRECTORY': "/home/%(uid)s",
                        'LOCKED_SHELL': "/usr/local/sbin/locked",
                        'NUMBER_SCHEME': 'default',
                        'LDAP_ACCOUNT_BASE': 'ou=Accounts,dc=example,dc=org',
                        'LDAP_GROUP_BASE': 'ou=Groups,dc=example,dc=org',
                  },
             ],
             'dummy': [
             ],
        }

#.  (optional) If you require people to be recorded in LDAP, add the
    :setting:`GLOBAL_DATASTORES` setting to ``/etc/karaage3/settings.py``:

    .. code-block:: python

        GLOBAL_DATASTORES = [
              {
                    'DESCRIPTION': 'LDAP datastore',
                    'ENGINE': 'karaage.datastores.ldap.GlobalDataStore',
                    'LDAP': 'default',
                    'PERSON': 'karaage.datastores.ldap_schemas.openldap_person',
                    'GROUP': 'karaage.datastores.ldap_schemas.openldap_person_group',
                    'NUMBER_SCHEME': 'global',
                    'LDAP_PERSON_BASE': 'ou=People,dc=example,dc=org',
                    'LDAP_GROUP_BASE': 'ou=People_Groups,dc=example,dc=org',
              },
        ]

    For best results the base settings should be different for the
    :setting:`GLOBAL_DATASTORES` and the :setting:`MACHINE_CATEGORY_DATASTORES`
    settings.

#.  Reload apache.

    .. code-block:: bash

        service apache2 reload
        service python-karaage-celery restart

#.  Log into web interface and add a machine category that references the ldap
    datastore. This should automatically populate LDAP with any entries you
    have created.

#.  Add missing LDAP entries:

    .. code-block:: bash

        kg-manage migrate_ldap
