Plugins
=======
There are a number of plugins for Karaage that are not enabled by default.

* Karaage Applications: application process for karaage.
* Karaage Software: keep track of software.
* Karaage Usage: keep track of usage.


Karaage Usage plugin
--------------------
Karaage usage requires karaage applications and karaage software, and will
automatically pull in the required dependancies. It is an external plugin that
provides usage graphs and statistics for cluster systems. To enable it:

#.  Install the extra required package:

    .. code-block:: bash

        apt-get install python-kgusage

#.  Add the following to ``/etc/karaage3/settings.py``:

    .. code-block:: python

        PLUGINS = [
            'karaage.plugins.kgusage.plugin',
        ]

#.   Run the database migrations, restart apache, and install the celery
     deaemon.

     .. code-block:: bash

        kg-manage migrate --all
        service apache2 reload
        apt-get install karaage3-celery

#.  Check to ensure the celery daemon is running.

You may need to update PBS/slurm logging to talk correctly to Karaage.  Only do
this if kg-pbs-logger was previously configured.

..  versionadded:: 3.0.1

    Karaage no longer requires a dedicated account for kg-pbs-logger. Rather it
    uses the machine entry.

For every machine:

-  Navigate to machine entry in admin website.

-  Click password button to reset the password.

-  Update ``/etc/karaage/pbs-logger.cfg`` and for ``ws_username`` use the
   machine name in karaage, and for ``ws_password`` use the password obtained
   in the previous step.

-  Test.
