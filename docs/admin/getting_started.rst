Getting Started
===============
This section is for administrators who don't already have Karaage installed and
wish to get started for the first time.

If you do have an older version of Karaage already installed, please see the
:doc:`upgrading` section.


Assumptions
-----------
Assumptions made by this documentation. Other configurations are possible,
however you will have to adapt from this documentation.

* You have a cluster running Slurm or PBS that is already up and running.
* You want to OpenLDAP with ppolicy support, on the same server.
* You have a Debian Wheezy server already setup for Karaage.
* You will be installing all components on a single system.


Installation
------------
#.  If you require a proxy server for out going connections, set it up now.

    .. code-block:: bash

        export http_proxy=http://proxy.example.org

#.  You need to install the VPAC Debian Archive signing key:

    .. code-block:: bash

        wget http://code.vpac.org/debian/vpac-debian-key.gpg -O - | apt-key add -

#.  Create a /etc/apt/sources.list.d/vpac.list containing::

        deb     http://code.vpac.org/debian  wheezy main
        deb-src http://code.vpac.org/debian  wheezy main

#.  Update your apt database and install the packages:

    .. code-block:: bash

        apt-get update

.. todo::

    CENTOS

    Add the VPAC CentOS repo

    wget http://code.vpac.org/centos/vpac.repo -O /etc/yum.repos.d/vpac.repo


MySQL server installation
-------------------------

#.  Run the following commands:

    .. code-block:: bash

        apt-get install mysql-server

    This should ask for a password for the root mysql user. Make sure this is a
    secure password. You can use makepasswd if you want. For the purpose of
    this documentation, we will assume you used XXXXXXXX. Do not use XXXXXXXX
    for your password on a production system.

#.  (optional) Create a /root/.my.cnf file containing::

        [client]
        user            = root
        password        = XXXXXXXX

#.  Create a /etc/mysql/conf.d/karaage.cnf file containing::

        [mysqld]
        character_set_server=utf8
        default-storage-engine = innodb
        sql_mode = STRICT_ALL_TABLES

        [client]
        default-character-set = utf8

    Note: these settings may affect other applications that use this database.

#.  Restart mysql server to load config:

    .. code-block:: bash

        service mysql reload

#.  Create a user and database for karaage::

        mysql> create database karaage;
        mysql> CREATE USER 'karaage'@'localhost' IDENTIFIED BY 'YYYYYYYY';
        mysql> GRANT ALL PRIVILEGES ON karaage.* TO 'karaage'@'localhost';

    Use the values you set in karaage settings. Do not use YYYYYYYY on a
    production system.


Initial setup
-------------

#.  Install the packages:

    .. code-block:: bash

        apt-get install karaage3-admin
        apt-get install karaage3-registration
        apt-get install python-mysqldb
        apt-get install libapache2-mod-wsgi

    If you have disabled installing recommended packages by default, you will
    need to install these packages by hand:

    .. code-block:: bash

        apt-get install rabbitmq-server
        apt-get install karaage3-celery

#.  Run kg_set_secret_key, this will automatically set SECRET_KEY inside /etc/karaage/global_settings.py

    .. code-block:: bash

         kg_set_secret_key

#.  Edit the DATABASES setting in /etc/karaage/global_settings.py:

    .. code-block:: python

         DATABASES = {
              'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': 'karaage',
                    'USER': 'karaage',
                    'PASSWORD': 'YYYYYYYY',
                    'HOST': 'localhost',
                    'PORT': '',
                    'ATOMIC_REQUESTS': True,
              }
         }

#.  Add ALLOWED_HOSTS = [ "hostname" ] to /etc/karaage/global_settings.py.
    Replace hostname with the visible hostname of your server.

#.  Update other settings in /etc/karaage/global_settings.py as required.

#.  Create DB tables:

    .. code-block:: bash

        kg-manage syncdb --noinput
        kg-manage migrate --all
        service karaage3-celery restart

#.  Create a karaage superuser:

    .. code-block:: bash

        kg-manage kgcreatesuperuser

    (do not use kg-manage createsuperuser, that doesn't exist.)

#.  Setup cron job. Edit the /etc/cron.d/karaage3-admin file::

        10 1 * * * www-data /usr/sbin/kg-daily-cleanup

#.  Setup symlink in apache conf.

    .. code-block:: bash

        ln -s /etc/karaage/kgadmin-apache.conf /etc/apache2/conf.d
        ln -s /etc/karaage/kgreg-apache.conf /etc/apache2/conf.d
        service apache2 reload

#.  Test. You should now be able to go to http://hostname/kgadmin/

#.  You should set up apache to use SSL.


Data stores
-----------
So far you have not configured any external datastores. Karaage will work,
however probably won't do anything useful. See the next section to configure
datastores (:doc:`datastores`).
