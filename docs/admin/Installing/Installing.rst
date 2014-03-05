Installing Karaage
==================

Karaage is currently supported on Debian Squeeze and Debian Wheezy.
Wheezy is preferred.

This instructions are currently for 2.7.x. Some changes will be required
for 3.x.x.

Prerequisites
-------------

-  A Database server (MySQL recommended) see
   http://docs.djangoproject.com/en/1.3/topics/install/#database-installation
   for others
-  An LDAP server installed with a user set up that has read/write
   access to users and groups tree. Both OpenLDAP and 389 have been
   tested. AD should also work, however currently might require a bit of
   extra work. OpenLDAP is recommended.

Which Karaage?
--------------

Karaage as two web interfaces

-  KaraageAdmin - Designed for use by admins of the system
-  karaage-registration - Designed for use by users of the system

Each Install needs to have karaage-admin installed on one host. You can
install karaage-registration on the same host or on a different host (or
not at all)

Installing
----------

1. Add the repositories to your system. See :doc:`Instructions <Packages>`.

2. Install the required packages:

   ::

       yum install karaage-admin
       yum install karaage-registration

       aptitude install karaage-admin
       aptitude install karaage-registration

Configuring
-----------

0. Run kg\_set\_secret\_key, this will automatically set SECRET\_KEY
   inside /etc/karaage/global\_settings.py

   ::

       kg_set_secret_key

1. Edit the file /etc/karaage/global\_settings.py

2. Create a user and database for karaage

   ::

       mysql> create database karaage;
       mysql> CREATE USER 'karaage'@'<hostname>' IDENTIFIED BY 'XXXXXXXX';
       mysql> GRANT ALL PRIVILEGES ON karaage.* TO 'karaage'@'<hostname>';

   Use the values you set in karaage settings.

3. Setup OpenLDAP/DirectoryServices/ActiveDirectory.

   Configure OpenLDAP for ppolicy and create initial LDAP administrator.
   See :doc:`instructions <OpenLDAP>`.

   To create the LDAP\_USER\_BASE and LDAP\_GROUP\_BASE OUs you can use
   the helper script

   ::

       kg-manage init_ldap

4. Ensure transactions are enabled. If you are using MySQL you should be
   using the InnoDB backend. This should be configured by default in
   recent installs. If you are using MyISAM transactions will not work.
   If you get past step 5 and find you have MyISAM, see
   [[Advanced/Transactions]] for instructions on how to convert existing
   tables.

5. Create DB tables. If asked to make a super user SAY NO

   ::

       kg-manage syncdb --noinput
       kg-manage migrate --all

6. Create a karaage superuser. NOTE: This will create an ldap account
   for you.

   ::

       kg-manage kgcreatesuperuser

   (do not use kg-manage createsuperuser, that won't do the complete job
   of setting everything up)

7. Setup cron job. You should add a cron job running as the user that
   runs Karaage, probably www-data, which runs
   ``/usr/sbin/kg-daily-cleanup``

8. Setup Apache/ Symlink in apache conf. Eg. on CentOS

   ::

       ln -s /etc/karaage/kgadmin-apache.conf /etc/httpd/conf.d/karaage-admin.conf

9. Test. You should now be able to go to

   ::

       http://hostname/kgadmin/

   You should set up apache to use SSL.

Karaage Admin
-------------

The interface is intended to be used by site admins only

Karaage Registration
--------------------

This site is intended to be used by end users of your systems.

It allows logged in users to

-  Edit their profile
-  Change their password
-  Accept software licenses for restricted software
-  Change their default project
-  Apply to join existing projects
-  Apply to start a new project

Unauthenticated users can apply for accounts and projects if this
feature is enabled

To enable registrations add the following to
/etc/karaage/registration\_settings.py

::

    ALLOW_REGISTRATIONS = True

By default usage information is private and only available to people who
are in the project

To allow anyone to view usage information add the following to
/etc/karaage/registration\_settings.py

::

    USAGE_IS_PUBLIC = True

