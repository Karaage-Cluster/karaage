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

#.  Create a ``/etc/apt/sources.list.d/vpac.list`` containing::

        deb     http://code.vpac.org/debian  wheezy main
        deb-src http://code.vpac.org/debian  wheezy main

#.  Update your apt database and install the packages:

    .. code-block:: bash

        apt-get update

.. todo::

    CENTOS

    Add the VPAC CentOS repo

    wget http://code.vpac.org/centos/vpac.repo -O /etc/yum.repos.d/vpac.repo


Apache Configuration
--------------------

Karaage, by default, requires a https connection. While this default can be
changed, this is not advisable on a production system.

In the following steps, replace ``www.example.org`` with the visible hostname
of your server.

#.  Install apache2.

    .. code-block:: bash

        apt-get install apache2

#.  Generate a SSL private key, a CSR.

    .. code-block:: bash

        cd /etc/apache2/ssl
        openssl genrsa -out www_privatekey.pem 2048
        chmod 700 www_privatekey.pem
        openssl req -new -key www_privatekey.pem -out www_csr.pem -sha256

#.      Submit www_csr.pem to a CA, and get it signed. Copy resultant
        certificate into ``www_cert.pem``. Check this file is sha256:

        .. code-block:: bash

            openssl x509 -text -noout -in www_cert.pem

        You should see the following text::

            Signature Algorithm: sha256WithRSAEncryption.

        You may need an intermediate certificate too. Copy this into
        ``www_intermediate.pem``.

#.      Setup Apache to support secure https connections. Changes should be
        made to ``/etc/apache2/sites-available/default-ssl``::

            SSLCertificateFile /etc/apache2/ssl/www_cert.pem
            SSLCertificateKeyFile /etc/apache2/ssl/www_privatekey.pem
            SSLCertificateChainFile /etc/apache2/ssl/www_intermediate.pem

        For more details on what changes are required, see the `Apache howto
        <http://httpd.apache.org/docs/current/ssl/ssl_howto.html>`_.

#.      Connections to http should be redirected to https.  Please replace the
        ``/etc/apache2/sites-available/default`` file entirely with the
        following::

            <VirtualHost *:80>
                ServerName www.example.org
                Redirect permanent / https://www.example.org/
            </VirtualHost>

        For more information on this step,
        see the `Apache wiki <https://wiki.apache.org/httpd/RedirectSSL>`_.

#.      (optional) It is recommended that you change the following settings in
        ``/etc/apache2/mods-enabled/ssl.conf`` to make SSL more secure by
        disabling insecure protocols and ciphers::

           SSLProtocol all -SSLv2 -SSLv3
           SSLCipherSuite ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA

        Note however that the ``SSLProtocol`` will break IE6, and the
        ``SSLCipherSuite`` setting will break IE on XP. For more information on
        securing Apache, see the `Mozilla website
        <https://wiki.mozilla.org/Security/Server_Side_TLS>`_.

#.      Enable ``default-ssl`` with the following commands:

        .. code-block:: bash

            a2enmod ssl
            a2ensite default-ssl.
            service apache2 restart

#.      Test by loading both ``http://www.example.org/`` and
        ``https://www.example.org/`` in your browser.

#.      Test website with `SSL Test
        <https://www.ssllabs.com/ssltest/index.html>`_.


MySQL configuration
-------------------

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

        kg-manage migrate

#.  Create a karaage superuser using :djadmin:`kgcreatesuperuser`:

    .. code-block:: bash

        kg-manage kgcreatesuperuser

#.  Setup cron job to automatically start :djadmin:`daily_cleanup`. Edit the
    ``/etc/cron.d/karaage3-database file``::

        10 1 * * * www-data /usr/bin/kg-manage daily_cleanup

#.  Test. You should now be able to go to ``http://www.example.org/karaage/``.


Data stores
-----------
So far you have not configured any external datastores. Karaage will work,
however probably won’t do anything useful. See the next section to configure
datastores (:doc:`datastores`).


Plugins
-------
For information on configuring additional plugins, see :doc:`plugins`.


Cluster tools
-------------
If installing Karaage on a cluster, you may want to install the cluster tools,
see :doc:`cluster`.
