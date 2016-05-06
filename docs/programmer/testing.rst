Testing Karaage
===============
This section talks about the steps involved in creating a new official
release of Karaage.

It is assumed the system is running Debian Jessie; other build systems may be
possible, but will require variations.

Preparing system
----------------
#.  Follow the instructions under :doc:`prepare`.

#.  Install karaage-test.

    .. code-block:: bash

        cd tree/karaage
        git clone https://github.com/Karaage-Cluster/karaage.git
        git clone https://github.com/Karaage-Cluster/karaage-test.git
        cd karaage-test

#.  Edit ``dotest.ini``, update pathes to reflect true location.

Automatically getting test data
-------------------------------

#.  Run a command like:

    .. code-block:: bash

        cd tree/karaage/karaage-test
        ./getdata -n vpac -s db1.vpac.org -l ldap1.vpac.org

    This will create the following large files:

    *   ``data/vpac/complete.ldif``
    *   ``data/vpac/complete.sql``
    *   ``data/vpac/nousage.sql``
    *   ``data/vpac/onlyusage.sql``

    The ``data`` directory can be a symlink if required.

#.  Create additional LDAP ldif files by hand. Samples below are for openldap.

    *   ``data/vpac/complete-config.ldif`` gets loaded first, so ensure that
        the LDAP configuration is appropriate for this data.

        .. code-block:: ldif

            dn: olcDatabase={1}mdb, cn=config
            changetype: modify
            replace: olcSuffix
            olcSuffix: dc=vpac,dc=org
            -
            replace: olcRootDN
            olcRootDN: cn=admin,dc=vpac,dc=org
            -
            replace: olcAccess
            olcAccess: {0}to attrs=userPassword,shadowLastChange by anonymous auth by dn="cn=admin,dc=vpac,dc=org" write by * none
            olcAccess: {1}to dn.base="" by * read
            olcAccess: {2}to * by dn="cn=admin,dc=vpac,dc=org" write by * read
            -

            dn: cn=module,cn=config
            changetype: add
            objectClass: olcModuleList
            cn: module
            olcModulepath: /usr/lib/ldap
            olcModuleload: ppolicy

            dn: olcOverlay=ppolicy,olcDatabase={1}mdb,cn=config
            changetype: add
            objectClass: olcPPolicyConfig
            olcPPolicyDefault: cn=default,ou=policies,dc=vpac,dc=org

    *   ``data/vpac/settings.py`` for telling Karaage the appropriate settings
        to use to access the LDAP data. Make sure that ``_ldap_password`` is
        correct.

        .. code-block:: ldif

            _ldap_base = 'dc=vpac,dc=org'
            _ldap_old_account_base = 'ou=people,%s' % _ldap_base
            _ldap_old_group_base = 'ou=groups,%s' % _ldap_base

            #_ldap_person_base = 'ou=people,%s' % _ldap_base
            #_ldap_person_group_base = 'ou=people_groups,%s' % _ldap_base

            _ldap_person_base = None
            _ldap_person_group_base = None

            _ldap_account_base = 'ou=people,%s' % _ldap_base
            _ldap_account_group_base = 'ou=groups,%s' % _ldap_base

            #_ldap_person_base = 'ou=people,%s' % _ldap_base
            #_ldap_person_group_base = 'ou=people,%s' % _ldap_base
            #_ldap_account_base = 'ou=accounts,%s' % _ldap_base
            #_ldap_account_group_base = 'ou=accounts,%s' % _ldap_base

            _ldap_user = 'cn=admin,%s' % _ldap_base
            _ldap_password = 'XXXXX'


Testing Karaage in schroot
--------------------------
Examples for running tests in a schroot:

*  Display help information:

   .. code-block:: ldif

       ./dotest --help

*  Create Karaage from last release available at linuxpenguins.xyz, install with
   empty data, and create super user.

   .. code-block:: ldif

       ./dotest --distribution jessie --architecture amd64 --shell --create_superuser

   The ``--shell`` option means that we open up a shell instead of immediately
   destroying the schroot when we finished.

*  Same as above, but build packages from local git source.

   .. code-block:: ldif

       ./dotest --distribution jessie --architecture amd64 --shell --source=local

*  Build test Karaage from copy of production data, and run full set of
   migrations, including south migrations.

   .. code-block:: ldif

       ./dotest --distribution jessie --architecture amd64 -k
       data/vpac/settings.py -L data/vpac/complete.ldif  -S
       data/vpac/nousage.sql --south --shell


Testing Karaage in Vagrant
--------------------------
Assumption: using virtualbox, and virtualbox already installed.

#.  Load vagrant Jessie image:

    .. code-block:: ldif

        vagrant box add jessie https://github.com/holms/vagrant-jessie-box/releases/download/Jessie-v0.1/Debian-jessie-amd64-netboot.box

    See http://www.vagrantbox.es/ for more available VMs.

#.  Change to vagrant directory:

    .. code-block:: ldif

        cd vagrant

#.  Check the ``Vagrantfile`` and ``bootstrap.sh`` config files.

#.  Bring VM up:

    .. code-block:: ldif

        vagrant up
        vagrant ssh
        sudo -s

#.  If you want to connect to VM without using vagrant's port forwarding, you
    may need to alter the ``HTTP_HOST`` setting in
    ``/etc/karaage3/settings.py``.
