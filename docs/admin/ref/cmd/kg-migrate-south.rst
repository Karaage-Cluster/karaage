kg-migrate-south
================
This command will install the latest South migrations.

Description
-----------
This command will install Django 1.6 and south in a virtualenv and then run
kg-manage migrate to run all South migrations.

This command should not be run except from upgrades from Django 1.6 or earlier.

All options supported by the django south migrate command can be used here.
