.. index:: pair: data store;openldap
Adding OpenLDAP
===============

Assumptions
-----------
You will need to substitute correct values for the following when applicable:

*  Base DN: dc=example,dc=org
*  Administrator DN: cn=admin,dc=example,dc=org
*  Administrator password: XXXXXXXX (do not use XXXXXXXX).


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

#.  Edit olcDatabase={2}bdb.ldif, and update/add the following values. Do not change anything else::

        olcSuffix: dc=example,dc=org
        olcRootDN: cn=admin,dc=example,dc=org
        olcRootPW: {SSHA}4bxi0+aXeYvv2TGT10VWUIwcaynqBbxH

    .. todo::

        olcTLSCertificateFile: /etc/.../cert.pem
        olcTLSCertificatekeyFile: /etc/.../key.pem

#.  Edit olcDatabase={1}monitor.ldif, and update update the admin DN. Do not change anything else::

        olcAccess: {0}to *  by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=externa
         l,cn=auth" read  by dn.base="cn=admin,dc=example,dc=org" read  by * none

    .. todo::

        #. Edit /etc/sysconfig/ldap::

                SLAPD_LDAPS=yes

#.  Run the following commands:

    .. code-block:: bash

        service slapd start
        chkconfig slapd on

#.  Create the file with the following contents in /tmp/ppolicy.ldif::

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

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy.ldif

#.  Create the file with the following contents in /tmp/ppolicy.ldif::

        dn: cn=module,cn=config
        objectClass: olcModuleList
        cn: module
        olcModulepath: /usr/lib/ldap
        olcModuleload: ppolicy.so

        dn: olcOverlay=ppolicy,olcDatabase={1}hdb,cn=config
        objectClass: olcPPolicyConfig
        olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy.ldif


Debian installation
---------------------

#.  Run the following commands:

    .. code-block:: bash

        apt-get install slapd
        apt-get install ldap-utils

    Enter XXXXXXXX when prompted for administrator's password.

#.  Create the file with the following contents in /tmp/ppolicy.ldif::

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

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy.ldif

#.  Create the file with the following contents in /tmp/ppolicy.ldif::

        dn: cn=module,cn=config
        objectClass: olcModuleList
        cn: module
        olcModulepath: /usr/lib/ldap
        olcModuleload: ppolicy.so

        dn: olcOverlay=ppolicy,olcDatabase={1}hdb,cn=config
        objectClass: olcPPolicyConfig
        olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

#.  Import with the following command:

    .. code-block:: bash

        ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy.ldif

.. todo::

    REPLICATION

    SSL

    CENTOS REPLICATION

    See http://itdavid.blogspot.com.au/2012/06/howto-openldap-24-replication-on-centos.html


Configuring Karaage to use LDAP
-------------------------------
#.  Add the following to /etc/karaage/global_settings.py:

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


#.  Reload apache.

    .. code-block:: bash

        service apache2 reload
        service karaage3-celery restart

#.  Log into web interface and add a machine category that references the ldap
    datastore. This should automatically populate LDAP with any entries you have
    created.
