kg-migrate-south
================
This command will install the latest South migrations.

Description
-----------
This command will install Django 1.6 and south in a virtualenv and then run
kg-manage migrate to run all South migrations.

After running this command, it should then be safe to run :djadmin:`migrate` to
run the Django 1.7 migrations.

This command should not be run except from upgrades from Django 1.6 or earlier
to Django 1.7.

All options supported by the django south migrate command can be used here.

Requirements
------------
This command requires virtualenv to be installed. On Debian Jessie install it
with:

.. code-block:: bash

   apt-get install virtualenv

On Debian jessie install it with:

.. code-block:: bash

   apt-get install python-virtualenv
