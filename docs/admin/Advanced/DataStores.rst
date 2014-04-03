Data Stores
===========

Karaage stores most of its data in a relational database. It can also
store user, account and group information in various data stores.

By default karaage uses the openldap datastore.

Datastore Types
---------------

Personal
~~~~~~~~

This is where personal information like name, email phone etc. is
stores.

This is set with the PERSONAL\_DATASTORE setting

Account
~~~~~~~

Where cluster account information is stored

Setting: ACCOUNT\_DATASTORES

This is a dictionary of :

This means if you have multiple machine categories you can store account
details in more than one location. (advanced)

Eg. Machine Category 1 stores accounts in LDAP. Machine Category 2 stores
accounts in Files.

NOTE:

*  This needs to use the same backend as personal type.
*  Currently no way to use different LDAPs for different MachineCategories
   as no way to specify different settings.

Institute
~~~~~~~~~
Create a group per institute.

By default karaage will create a group per institute. The GID number is
stored in the DB and linked against the group. This means you can change
the name of the group if needed.

INSTITUTE\_DATASTORE

Project
~~~~~~~

Create a group per project

By default karaage will create a group per project using the project PID
as the name of the group

PROJECT\_DATASTORE

Software
~~~~~~~~

Create a group per software

By default karaage will create a group per software package. The GID
number is stored in the DB and linked against the group. This means you
can change the name of the group if needed. SOFTWARE\_DATASTORE


Datastore backends
------------------

OpenLDAP (Default)
~~~~~~~~~~~~~~~~~~

This is the default

For openldap

Settings: (Note for some use LDAP Data Store as they are compatible)

::

    PERSONAL_DATASTORE = 'karaage.datastores.openldap_datastore'
    PROJECT_DATASTORE = 'karaage.datastore.projects.ldap_datastore'
    INSTITUTE_DATASTORE = 'karaage.datastore.institutes.ldap_datastore'
    SOFTWARE_DATASTORE = 'karaage.datastore.software.ldap_datastore'

LDAP (Directory Services) eg. Red Hat/CentOS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Same has openldap except for locking uses Directory Services style
locking of accounts.

Settings: (Note for some use LDAP Data store as they are compatible)

::

    PERSONAL_DATASTORE = 'karaage.datastores.ldap_datastore'
    PROJECT_DATASTORE = 'karaage.datastore.projects.ldap_datastore'
    INSTITUTE_DATASTORE = 'karaage.datastore.institutes.ldap_datastore'
    SOFTWARE_DATASTORE = 'karaage.datastore.software.ldap_datastore'

Required setting:

::

    LDAP_LOCK_DN = 'DN of locked user role'

Active Directory
~~~~~~~~~~~~~~~~

Use MS Active Directory. Tested on 2003 and 2008R2

Settings: (Note for some use LDAP Data store as they are compatible)

::

    PERSONAL_DATASTORE = 'karaage.datastores.ad_datastore'
    PROJECT_DATASTORE = 'karaage.datastore.projects.ldap_datastore'
    INSTITUTE_DATASTORE = 'karaage.datastore.institutes.ldap_datastore'
    SOFTWARE_DATASTORE = 'karaage.datastore.software.ldap_datastore'

Files
~~~~~

Sore data in /etc/passwd files

NOTE: This is not fully implemented

Settings:

::

    PERSONAL_DATASTORE = 'karaage.datastores.files'

Required settings:

::

    PASSWD_FILES = ['/etc/passwd', '/usr/local/etc/passwd']

Dummy
~~~~~

Set to dummy to do nothing

::

    PERSONAL_DATASTORE = 'karaage.datastores.dummy'
    PROJECT_DATASTORE = 'karaage.datastore.projects.dummy'
    INSTITUTE_DATASTORE = 'karaage.datastore.institutes.dummy'
    SOFTWARE_DATASTORE = 'karaage.datastore.software.dummy'

