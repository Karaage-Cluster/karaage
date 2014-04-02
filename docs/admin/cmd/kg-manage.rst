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

Applications
------------

:command:`application_cleanup`
    Cleanup complete/old applications.

Django
------

:command:`clearsessions`
    Clean out expired sessions.

:command:`dbshell`
    Enter db shell for administration.

:command:`shell`
    Enter python shell for administration.

People
------

:command:`change_username`
    Change the username for a person and related accounts.

:command:`changepassword`
    Change the password for a person and related accounts.

:command:`import_csv_users`
    Import people from a csv file.

:command:`kgcreatesuperuser`
    Create a superuser without an account.

:command:`lock_expired`
    Automatically lock expired accounts.

:command:`lock_training_accounts`
    Automatically lock training accounts.

:command:`unlock_training_accounts`
    Automatically lock training accounts.


Projects
--------

:command:`change_pid`
    Change a PID for a project.


Usage
-----

:command:`clear_usage_cache`
    Delete the usage cache.

:command:`clear_usage_graphs`
    Delete the usagee graphs.

:command:`link_software`
    Automatically link software in usage table.
