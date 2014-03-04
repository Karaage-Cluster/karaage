Configuring OpenLDAP
====================

On Debian wheezy:

::

    apt-get install slapd
    apt-get install ldap-utils
    ldapadd -Y EXTERNAL -H ldapi:///  < /etc/ldap/schema/ppolicy.ldif

Create the file with the following contents in /tmp/ppolicy.ldif (note:
replace dc=example,dc=org with your base DN):

::

    dn: ou=policies,dc=example,dc=org
    objectClass: organizationalUnit

    dn: cn=default,ou=policies,dc=example,dc=org
    objectClass: top
    objectClass: device
    objectClass: pwdPolicy
    pwdAttribute: 2.5.4.35

Import with the following command:

::

    ldapadd -x -H ldapi:///  -D cn=admin,dc=example,dc=org -W < /tmp/ppolicy.ldif

Create the file with the following contents in /tmp/ppolicy.ldif (note:
replace dc=example,dc=org with your base DN):

::

    dn: cn=module,cn=config
    objectClass: olcModuleList
    cn: module
    olcModulepath: /usr/lib/ldap
    olcModuleload: ppolicy.so

    dn: olcOverlay=ppolicy,olcDatabase={1}hdb,cn=config
    objectClass: olcPPolicyConfig
    olcPPolicyDefault: cn=default,ou=policies,dc=example,dc=org

Import with the following command:

::

    ldapadd -Y EXTERNAL -H ldapi:///  < /tmp/ppolicy.ldif

