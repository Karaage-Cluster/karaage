Management commands
===================

Karaage comes with various management commands.

List of kg-manage commands
--------------------------

application\_cleanup
~~~~~~~~~~~~~~~~~~~~

Does some tidyup of applications.

-  Deletes all expired applications
-  Delete all Applications that have been in the state "Complete" for 1
   month

change\_username
~~~~~~~~~~~~~~~~

Changes a users username

clear\_usage\_cache
~~~~~~~~~~~~~~~~~~~

Clears the entire usage cache

gen\_usage\_cache
~~~~~~~~~~~~~~~~~

Generates usage cache values for last 7, 90 and 365 days

import\_csv\_users
~~~~~~~~~~~~~~~~~~

See :doc:`Guides on migrating to Karaage <Migration>`

kgcreatesuperuser
~~~~~~~~~~~~~~~~~

Should be used instead of the internal django createsuperuser command.

Creates a superuser in karaage. Only really needed for new installs.

link\_software
~~~~~~~~~~~~~~

Link software and usage from data stored in the usage\_usedmodules
table.

lock\_expired
~~~~~~~~~~~~~

Locks all expired users

kg-daily-cleanup
----------------

This command is designed to run nightly and is a combination of various
commands.

-  cleanup - An internal django command to clean up session data
-  lock\_expired
-  clear\_usage\_cache
-  gen\_usage\_cache
-  clear\_usage\_graphs
-  gen\_usage\_graphs
-  application\_cleanup
-  link\_software - run with yesterdays date as it's argument

