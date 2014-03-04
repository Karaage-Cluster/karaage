karaage-pbs-logger
==================

Installing
----------

Add the VPAC repo see :doc:`Packages`

Then

::

    yum install karaage-pbs-logger

OR

::

    aptitude install karaage-pbs-logger

Configuring
-----------

Edit /etc/karaage/pbs-logger.cfg

Example config

::

    [pbs-logger]
    # Machine name as specified in Karaage
    # Eg. macihine_name = tango
    machine_name = cluster21

    # Directory where PBS stores its accounting logs
    log_dir = /var/logs/torque/server_priv/accounting

    # Location of the xmlrpc interface for karaage. Must end with a /
    ws_url = https://example.org/kgadmin/xmlrpc/

    # Username and password for the karaage user.
    # Must have the permission 'projects.change_project'
    ws_username = dummyuser 
    ws_password = secret

Cron
----

By default the installation will set it self up to process yesterdays
log file at 4am each night.

Logging
-------

By default it will log to /var/log/karaage/pbs-logger.log

To print debugging info to the console pass the -d option

You can configure logging in /etc/karaage/logging.conf
