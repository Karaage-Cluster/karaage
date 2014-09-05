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

clearsessions
~~~~~~~~~~~~~
.. django-admin:: clearsessions

    Clean out expired sessions. See :djadmin:`django:clearsessions`.

dbshell
~~~~~~~
.. django-admin:: dbshell

    Enter db shell for administration. See :djadmin:`django:dbshell`.

shell
~~~~~
.. django-admin:: shell

    Enter python shell for administration. See :djadmin:`django:shell`.


Karaage Core
------------

migrate_ldap
~~~~~~~~~~~~
.. django-admin:: migrate_ldap

    Run migrations on LDAP servers.

.. django-admin-option:: --dry-run

   Don't make any of the changes, display what would be done instead. Note the
   base dn objects will always be created.

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


Karaage Applications Plugin
---------------------------

application_cleanup
~~~~~~~~~~~~~~~~~~~
.. django-admin:: application_cleanup

    Cleanup complete/old applications.



Karaage Usage Plugin
--------------------

clear_usage_cache
~~~~~~~~~~~~~~~~~
.. django-admin:: clear_usage_cache

    Delete the usage cache.

clear_usage_graphs
~~~~~~~~~~~~~~~~~~
.. django-admin:: clear_usage_graphs

    Delete the usagee graphs.

link_software
~~~~~~~~~~~~~
.. django-admin:: link_software

    Automatically link software in usage table.
