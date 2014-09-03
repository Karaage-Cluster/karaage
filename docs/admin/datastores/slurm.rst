.. index:: pair: data store; slurm

Adding Slurm
============

First configure the LDAP datastore. See :doc:`openldap`.

Edit the :setting:`MACHINE_CATEGORY_DATASTORES` setting in
``/etc/karaage3/settings.py``:

.. code-block:: bash

   MACHINE_CATEGORY_DATASTORES = {
       'ldap': [
           {
               'DESCRIPTION': 'Default LDAP datastore',
               ...
           },
           {
               'DESCRIPTION': 'Default Slurm datastore',
               'ENGINE': 'karaage.datastores.slurm.SlurmDataStore',
               'PREFIX': [ "sudo", "-uslurm" ],
               'PATH': "/usr/local/slurm/latest/bin/sacctmgr",
               'NULL_PROJECT': 'default',
           },
       ],
       'dummy': [
       ],
   }

Values ``PREFIX``, ``PATH``, and ``NULL_PROJECT`` are defaults and can be
omitted.

Reload apache.

.. code-block:: bash

   service apache2 reload
   service python-karaage-celery restart
