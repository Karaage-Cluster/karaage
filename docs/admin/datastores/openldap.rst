.. index:: pair: data store;openldap

Adding OpenLDAP
===============

Assumptions
-----------
You will need to substitute correct values for the following when applicable:

*  Base DN: ``dc=example,dc=org``
*  Administrator DN: ``cn=admin,dc=example,dc=org``
*  Administrator password: ``XXXXXXXX`` (do not use ``XXXXXXXX``).


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

    Enter XXXXXXXX twice. This should output an encrypted password starting with XXXXXXXX. Copy that into the clipboard.

    The result for XXXXXXXX is {SSHA}4bxi0+aXeYvv2TGT10VWUIwcaynqBbxH (do not use this value).

#.  Edit ``olcDatabase={2}bdb.ldif``, and update/add the following values. Do not change anything else::

        olcSuffix: dc=example,dc=org
        olcRootDN: cn=admin,dc=example,dc=org
        olcRootPW: {SSHA}4bxi0+aXeYvv2TGT10VWUIwcaynqBbxH

#.  Edit ``olcDatabase={1}monitor.ldif``, and update update the admin DN. Do not change anything else::

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
        olcTLSCertificateFile: /etc/ssl/private/hostcert.pem
        -
        replace: olcTLSCertificatekeyFile
        olcTLSCertificatekeyFile: /etc/ssl/private/hostkey.pem

    Any intermediate certicates need to be listed with ``olcTLSCACertificatePath``.

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ldapssl.ldif

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
        olcAccess: to attrs=userPassword,shadowLastChange by self write by anonymous auth by dn="cn=admin,dc=example,dc=org" write by * none
        olcAccess: to * by self write by dn="cn=admin,dc=example,dc=org" write by * read

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

.. todo::

    REPLICATION

    CENTOS REPLICATION

    See http://itdavid.blogspot.com.au/2012/06/howto-openldap-24-replication-on-centos.html


Debian installation
---------------------

#.  Run the following commands:

    .. code-block:: bash

        apt-get install slapd
        apt-get install ldap-utils

    Enter XXXXXXXX when prompted for administrator’s password.

#.  Create the file with the following contents in ``/tmp/ppolicy1.ldif``::

        dn: cn=module,cn=config
        objectClass: olcModuleList
        cn: module
        olcModulepath: /usr/lib64/openldap/
        olcModuleload: ppolicy.la

        dn: olcOverlay=ppolicy,olcDatabase={2}bdb,cn=config
        objectClass: olcPPolicyConfig
        olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy1.ldif

#.  Create the file with the following contents in ``/tmp/ppolicy2.ldif``::

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

        ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy2.ldif

.. todo::

    REPLICATION

    SSL


Configuring Karaage to use LDAP
-------------------------------
#.  Add the :setting:`LDAP` and :setting:`MACHINE_CATEGORY_DATASTORES` settings
    to ``/etc/karaage3/settings.py``:

    .. code-block:: python


        LDAP = {
             'default': {
                  'ENGINE': 'tldap.backend.fake_transactions',
                  'URI': 'ldap://localhost',
                  'USER': 'cn=admin,dc=example,dc=org',
                  'PASSWORD': 'XXXXXXXX',
                  'REQUIRE_TLS': False,
                  'START_TLS ': False,
                  'TLS_CA' : None,
             }
        }

        MACHINE_CATEGORY_DATASTORES = {
             'ldap': [
                  {
                        'DESCRIPTION': 'LDAP datastore',
                        'ENGINE': 'karaage.datastores.ldap.AccountDataStore',
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
    datastore. This should automatically populate LDAP with any entries you have
    created.
