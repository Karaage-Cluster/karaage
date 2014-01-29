.. index:: pair: data store; gold
.. index:: see:mam;gold

Adding Gold
===========

First configure the LDAP datastore. See :doc:`openldap`.

Edit DATASTORES in /etc/karaage/global_settings.py:

.. code-block:: bash

   DATASTORES = {
       'ldap' : [
           {
               'DESCRIPTION': 'Default LDAP datastore',
               ...
           },
           {
               'DESCRIPTION': 'Default Gold datastore',
               'ENGINE': 'karaage.datastores.gold.GoldDataStore',
               'PREFIX': [],
               'PATH': '/usr/local/gold/bin',
               'NULL_PROJECT': 'default',
           },
       ],
       'dummy' : [
       ],
   }

Values PREFIX, PATH, and NULL_PROJECT are defaults and can be omitted.

Reload apache.

.. code-block:: bash

   service apache2 reload
   service karaage3-celery restart
