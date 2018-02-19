.. index:: pair: data store; gold
.. index:: see:mam;gold

Adding MOAB Account Manager
===========================

#. First configure the LDAP datastore. See :doc:`openldap`.

#. Install mam command line.

#. Test using ``www-data`` user.

#. Add project to MAM that has no access. Call it ``default`` (or whatever
   else you want).

#. Edit the :setting:`DATASTORES` setting in
   ``/etc/karaage3/settings.py``:

   .. code-block:: python

      DATASTORES = [
          {
              'DESCRIPTION': 'LDAP datastore',
              ...
          },
          {
              'DESCRIPTION': 'MAM datastore',
              'ENGINE': 'karaage.datastores.mam.MamDataStore',
              'PREFIX': [],
              'PATH': '/usr/local/mam/bin:/usr/local/mam/sbin',
              'NULL_PROJECT': 'default',
          },
      ]

   Values ``PREFIX``, ``PATH``, and ``NULL_PROJECT`` are defaults and can be
   omitted.

#. In ``/etc/karaage3/settings.py`` uncomment the :setting:`LOGGING` assignment
   lines related to mam.

#. Reload apache.

   .. code-block:: bash

      service apache2 reload
      service python-karaage-celery restart
