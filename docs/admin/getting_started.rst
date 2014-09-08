Getting Started
===============
This section is for administrators who don’t already have Karaage installed and
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
* You are upgrading to Karaage 3.1.
* The visible hostname is ``www.example.org``. This will have to be
  changed as required.


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
    this documentation, we will assume you used ``XXXXXXXX``. Do not use
    ``XXXXXXXX`` for your password on a production system.

#.  (optional) Create a ``/root/.my.cnf`` file containing::

        [client]
        user            = root
        password        = XXXXXXXX

#.  Create a ``/etc/mysql/conf.d/karaage.cnf`` file containing::

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

    You will use the values you set, later, in the karaage settings. Do not use
    ``YYYYYYYY`` on a production system.


Initial setup
-------------

#.  Install the packages:

    .. code-block:: bash

        apt-get install karaage3
        apt-get install python-mysql.connector

#.  Karaage, by default, requires a https connection. While this default can be
    changed, this is not advisable on a production system.

    In the following steps, replace ``www.example.org`` with the visible
    hostname of your server.

    #.  Setup Apache to support secure https connections. Changes should be
        made to the ``/etc/apache2/sites-available/default-ssl``.  Read the
        comments in this file. For more details on what changes are required,
        see the `Apache howto
        <http://httpd.apache.org/docs/current/ssl/ssl_howto.html>`_.

    #.  Connections to http should be redirected to https.  Please replace the
        ``/etc/apache2/sites-available/default`` file entirely with the
        following::

            <VirtualHost *:80>
                ServerName www.example.org
                Redirect permanent / https://www.example.org/
            </VirtualHost>

        For more information on this step,
        see the `Apache wiki <https://wiki.apache.org/httpd/RedirectSSL>`_.

    #.  Enable ``default-ssl`` with the following commands:

        .. code-block:: bash

            a2enmod ssl
            a2ensite default-ssl.
            service apache2 restart

    #.  Test by loading both ``http://www.example.org/`` and
        ``https://www.example.org/`` in your browser.

#.  Run :doc:`/ref/cmd/kg-set-secret-key`, this will automatically set
    :setting:`SECRET_KEY` inside ``/etc/karaage3/settings.py``:

    .. code-block:: bash

         kg_set_secret_key

#.  Edit the :setting:`DATABASES` setting in ``/etc/karaage3/settings.py``:

    .. code-block:: python

         DATABASES = {
              'default': {
                    'ENGINE': 'mysql.connector.django',
                    'NAME': 'karaage',
                    'USER': 'karaage',
                    'PASSWORD': 'YYYYYYYY',
                    'HOST': 'localhost',
                    'PORT': '',
                    'ATOMIC_REQUESTS': True,
              }
         }

#.  Add the :setting:`HTTP_HOST` setting in ``/etc/karaage3/settings.py``:
    
    .. code-block:: python

       HTTP_HOST = "www.example.org"

    Replace ``www.example.org`` with the visible hostname of your server.

#.  Update other settings in ``/etc/karaage3/settings.py`` as required. See
    comments in this file and :doc:`/ref/settings`.

#.  Create DB tables:

    .. code-block:: bash

        kg-manage syncdb --noinput
        kg-manage migrate --all

#.  Create a karaage superuser using :djadmin:`kgcreatesuperuser`:

    .. code-block:: bash

        kg-manage kgcreatesuperuser

#.  Setup cron job. Edit the ``/etc/cron.d/python-karaage file``::

        10 1 * * * www-data /usr/bin/kg-daily-cleanup

#.  Test. You should now be able to go to ``http://www.example.org/kgadmin/``.


Data stores
-----------
So far you have not configured any external datastores. Karaage will work,
however probably won’t do anything useful. See the next section to configure
datastores (:doc:`datastores`).


Plugins
-------
For information on configuring additional plugins, see :doc:`plugins`.
