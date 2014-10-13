kg-manage
=========
This command is used for managing karaage.

Usage
-----

Basic usage:

.. code-block:: bash

   kg-manage <command> [options]

The following is not a complete list of all commands available.  To get a full
list of commands, run the following:

.. code-block:: bash

   kg-manage --help

To get help on a particular command, run the following:

.. code-block:: bash

   kg-manage <command> --help


Django
------

dbshell
~~~~~~~
.. django-admin:: dbshell

    Enter db shell for administration. See :djadmin:`django:dbshell`.

shell
~~~~~
.. django-admin:: shell

    Enter python shell for administration. See :djadmin:`django:shell`.

migrate
~~~~~~~
.. django-admin:: migrate

    Run migrations on database. See :djadmin:`django:migrate`.


Karaage Core
------------

migrate_ldap
~~~~~~~~~~~~
.. django-admin:: migrate_ldap

    Run migrations on LDAP servers.

.. django-admin-option:: --dry-run

   Don't make any of the changes, display what would be done instead. Note the
   base dn objects will always be created.

.. django-admin-option:: --delete

   Delete old records that are no longer used.

change_username
~~~~~~~~~~~~~~~
.. django-admin:: change_username

    Change the username for a person and related accounts.

changepassword
~~~~~~~~~~~~~~
.. django-admin:: changepassword

    Change the password for a person and related accounts.

import_csv_users
~~~~~~~~~~~~~~~~
.. django-admin:: import_csv_users

    Import people from a csv file.

kgcreatesuperuser
~~~~~~~~~~~~~~~~~
.. django-admin:: kgcreatesuperuser

    Create a superuser without an account.

lock_expired
~~~~~~~~~~~~
.. django-admin:: lock_expired

    Automatically lock expired accounts.

    Called automatically by :djadmin:`daily_cleanup`.

lock_training_accounts
~~~~~~~~~~~~~~~~~~~~~~
.. django-admin:: lock_training_accounts

    Automatically lock training accounts.

unlock_training_accounts
~~~~~~~~~~~~~~~~~~~~~~~~
.. django-admin:: unlock_training_accounts

    Automatically lock training accounts.

change_pid
~~~~~~~~~~
.. django-admin:: change_pid

    Change a PID for a project.

daily_cleanup
~~~~~~~~~~~~~
.. django-admin:: daily_cleanup

   Daily cleanup for Karaage, should be called by cron job. This will
   automatically call all other applicable cleanup commands.

   The exact commands executed depends on which plugins are configured.
   By default, will call :djadmin:`lock_expired`.


Karaage Applications Plugin
---------------------------

application_cleanup
~~~~~~~~~~~~~~~~~~~
.. django-admin:: application_cleanup

    Cleanup complete/old applications.

    Called automatically by :djadmin:`daily_cleanup`.


Karaage Usage Plugin
--------------------

clear_usage_cache
~~~~~~~~~~~~~~~~~
.. django-admin:: clear_usage_cache

    Delete the usage cache.

    Called automatically by :djadmin:`daily_cleanup`.

clear_usage_graphs
~~~~~~~~~~~~~~~~~~
.. django-admin:: clear_usage_graphs

    Delete the usagee graphs.

    Called automatically by :djadmin:`daily_cleanup`.

link_software
~~~~~~~~~~~~~
.. django-admin:: link_software

    Automatically link software in usage table.

    Called automatically by :djadmin:`daily_cleanup`.
