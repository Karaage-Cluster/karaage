Getting Started
===============

Requirements
------------
None of these requirements are absolute requirements, however strongly
recommended as these are what have been extensively tested and documented:

* Cluster running Slurm or PBS (assumed to be already up and running).
* OpenLDAP with ppolicy support. 389 or AD might also work.
* Debian Wheezy server for Karaage.


Installation
------------
1. First you need to install the VPAC Debian Archive signing key:

   .. code-block:: bash

      wget http://code.vpac.org/debian/vpac-debian-key.gpg -O - | apt-key add -

2. Then create a /etc/apt/sources.list.d/vpac.list containing::

      deb     http://code.vpac.org/debian  wheezy main
      deb-src http://code.vpac.org/debian  wheezy main

3. Then update your apt database and install the packages:

   .. code-block:: bash

      apt-get update
      apt-get install karaage-admin
      apt-get install karaage-registration

.. todo::

   auto start celeryd

   CENTOS

   Add the VPAC CentOS repo

   wget http://code.vpac.org/centos/vpac.repo -O /etc/yum.repos.d/vpac.repo


MySQL server installation
-------------------------

1. Run the following commands:

   .. code-block:: bash

      apt-get install mysql-server

2. Create a /etc/mysql/conf.d/karaage.cnf file containing::

      [mysqld]
      character_set_server=utf8
      default-storage-engine = innodb
      sql_mode = STRICT_ALL_TABLES

      [client]
      default-character-set = utf8

3. Restart mysql server to load config:

   .. code-block:: bash

      service apache2 reload

3. Create a user and database for karaage::

      mysql> create database karaage;
      mysql> CREATE USER 'karaage'@'localhost' IDENTIFIED BY 'XXXXXXXX';
      mysql> GRANT ALL PRIVILEGES ON karaage.* TO 'karaage'@'localhost';

   Use the values you set in karaage settings.


Initial setup
-------------

1. Run kg_set_secret_key, this will automatically set SECRET_KEY inside /etc/karaage/global_settings.py

   .. code-block:: bash

       kg_set_secret_key

2. Edit the DATABASES setting in /etc/karaage/global_settings.py:

   .. code-block:: python

       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.mysql',
               'NAME': 'karaage',
               'USER': 'karaage',
               'PASSWORD': 'XXXXXXXX',
               'HOST': 'localhost',
               'PORT': '',
               'ATOMIC_REQUESTS': True,
           }
       }

3. Add ALLOWED_HOSTS = [ "hostname" ] to /etc/karaage/global_settings.py.
   Replace hostname with the visible hostname of your server.

3. Update other settings in /etc/karaage/global_settings.py as required.

4. Create DB tables:

   .. code-block:: bash

      kg-manage syncdb --noinput
      kg-manage migrate --all

5. Create a karaage superuser:

   .. code-block:: bash

      kg-manage kgcreatesuperuser

   (do not use kg-manage createsuperuser, that doesn't exist.)

6. Setup cron job. You should add a cron job running as the user that runs
   Karaage, probably www-data, which runs /usr/sbin/kg-daily-cleanup

7. Setup symlink in apache conf.

   .. code-block:: bash

      ln -s /etc/karaage/kgadmin-apache.conf /etc/apache/conf.d
      ln -s /etc/karaage/kgreg-apache.conf /etc/apache/conf.d
      service apache2 reload

8.  Test. You should now be able to go to http://hostname/kgadmin/

9.  You should set up apache to use SSL.


Data stores
-----------
So far you have not configured any external datastores. Karaage will work,
however probably won't do anything useful. See the next section to configure
datastores (:doc:`datastores`).
