Upgrading
=========
This section is for administrators who have an older version of Karaage already
installed, and wish to upgrade.

If you don't already have Karaage installed and wish to get started for the
first time, please see the :doc:`upgrading` section.


Assumptions
-----------
It is assumed you are already running the latest karaage 2.7.x release. You
should already be running at least Django 1.6.  If this is not the case, please
upgrade using the procedure at
`old documentation <https://github.com/Karaage-Cluster/karaage/wiki/Upgrading>`_.


Upgrading to Version 3.0.x
--------------------------
The following applies if you want to upgrade from 2.7.x to 3.0.x.

.. warning::

    This is a non-trivial upgrade with non-trivial database migrations. The
    database migrations will take some time to complete and could fail or cause
    data loss. It is recommended that you copy your production data and run the
    database migrations on a test system, as shown below.

.. warning::

    Some of the following steps should never be executed on the production box.
    Double check which box you are working on at all times.

.. note::

    If you do encounter any problems performing database migrations, please file
    a bug report, so the problem can be fixed. Bug reports can be submitted at
    `github <https://github.com/Karaage-Cluster/karaage/issues>`_.

#.  Setup a test system. If possible, should have same version of LDAP server as
    your production box, as this will simplify copying your LDAP database.

    Read the steps in :doc:`getting_started`. Do not set up any data stores
    yet.

#.  Dump data on production box:

    #.  Dump mysql database on production box.

        .. code-block:: bash

            mysqldump karaage > karaage.sql

    #.  Dump LDAP database on production box.

        .. code-block:: bash

            slapcat > karaage.ldif

#.  Stop karaage processes on test box.

    .. code-block:: bash

        service apache2 stop
        service karaage3-celery stop

#.  Import data into mysql on test system:

    .. warning::

        Don't do this on production box!

    #.  Drop karaage database::

            mysql> drop database karaage

    #.  Import mysql database on test box.

       .. code-block:: bash

            mysql < karaage.sql

    #.  Ensure all tables in database are using innodb and utf8 encoding::

            mysql> use karaage
            mysql> show table status

        For every table that is not innodb, convert it with::

            mysql> ALTER TABLE table_name ENGINE=InnoDB;

        For every table that is not utf8, convert it with::

            mysql> ALTER TABLE table_name CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci

        Some of these conversions may take some time to complete, especially
        for the cpujob table.

#.  Import data into openldap on test system:

    .. warning::

        Don't do this on production box!

    #.  Install LDAP server:

        .. code-block:: bash

            apt-get install slapd
            service slapd stop

    #.  Copy entire LDAP config from production box to test box. e.g.

        .. code-block:: bash

            rsync -avP --delete testbox:/etc/ldap /etc

    #.  Import LDAP data.

        .. code-block:: bash

            rm -rf /var/lib/ldap/*
            slapadd < karaage.ldif
            chown openldap:openldap -R /var/lib/ldap

    #.  Restart LDAP server:

        .. code-block:: bash

            service slapd start

#.  Ensure both mysql and LDAP data are correct without any obvious signs of problems.

#.  Check the following settings are in /etc/karaage/global_settings.py:

    .. code-block:: python

         DATABASES = {
              'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': 'karaage',
                    'USER': 'karaage',
                    'PASSWORD': 'XXXXXXXX',
                    'HOST': 'localhost',
                    'PORT': '',
                    'ATOMIC_REQUESTS': True,
              }
         }

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

#.  Migrate DB tables:

    .. code-block:: bash

        kg-manage migrate --all

    Some of these migrations may take some time to complete.

#. If you have any other datastores, configure them now (:doc:`datastores`).

#.  Restart karaage processes.

    .. code-block:: bash

        service apache2 start
        service karaage3-celery start

#.  Test. You should now be able to go to http://hostname/kgadmin/

#.  If you are happy with the results, make this test box your new production
    box.
