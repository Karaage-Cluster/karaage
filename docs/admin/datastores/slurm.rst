Adding Slurm
============

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
               'DESCRIPTION': 'Default Slurm datastore',
               'ENGINE': 'karaage.datastores.slurm.SlurmDataStore',
               'PREFIX': [ "sudo", "-uslurm" ],
               'PATH': "/usr/local/slurm/latest/bin/sacctmgr",
               'NULL_PROJECT': 'default',
           },
       ],
       'dummy' : [
       ],
   }

Values PREFIX, PATH, and NULL_PROJECT are defaults and can be omitted.
