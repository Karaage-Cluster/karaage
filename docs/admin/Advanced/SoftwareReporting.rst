Software Reporting (Beta)
=========================

*New in Karaage 2.6*

How it works?
-------------

There is a new database table called "usage\_usedmodules"

It has 2 fields. Jobid and modules.

You need to write a script that will insert data into this table.

Example \|\| jobid \|\| modules \|\| \|\| 123.cluster.com \|\|
gcc/4.2:beast/3.2:matlab/2 \|\| \|\| 124.cluster.com \|\| matlab/2.1
\|\|

Karaage will then parse this data nightly and link it to CPUJobs and
!SoftwareVersions. (Currently not enabled in nightly script - must run
by hand) You can also run this by hand see
[wiki:Advanced/ManagementCommands#link\_software ManagementCommands]

If it can't find a !SoftwareVersion with the corresponding module it
will create a new one. If it can link the data successfully it will
remove the row in the usage\_usedmodules table"

Ignoring some modules
~~~~~~~~~~~~~~~~~~~~~

To ignore reporting of specific modules add the following to your
karaage settings

::

    SOFTWARE_IGNORED_MODULES = [
        'modules',
        'ignoredmodule/2',
    ]

