.. index:: pair: data store; slurm

Adding Slurm
============

#. First configure the LDAP datastore. See :doc:`openldap`.

#. Install slurm command line.

#. Add to ``/etc/sudoers``:

   .. code-block:: text

      www-data ALL=(slurm) NOPASSWD: /usr/local/slurm/latest/bin/sacctmgr

#. Test using ``www-data`` user:

   .. code-block:: bash

      sudo -uslurm /usr/local/slurm/latest/bin/sacctmgr -ip

#. Add project to slurm that has no access. Call it ``default`` (or whatever
   else you want).

#. Edit the :setting:`MACHINE_CATEGORY_DATASTORES` setting in
   ``/etc/karaage3/settings.py``:

   .. code-block:: python

      MACHINE_CATEGORY_DATASTORES = {
          'ldap': [
              {
                  'DESCRIPTION': 'LDAP datastore',
                  ...
              },
              {
                  'DESCRIPTION': 'Slurm datastore',
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

#. In ``/etc/karaage3/settings.py`` uncomment the :setting:`LOGGING` assignment
   lines related to slurm.

#. Reload apache.

   .. code-block:: bash

      service apache2 reload
      service python-karaage-celery restart
