Adding machines
---------------

To add a machine, you need a machine category first.

.. index:: pair: machine category; adding

Creating Machine Category
=========================

A :term:`machine category` uses a :term:`data store`. This should already be
defined, as per instructions in the :doc:`/datastores` section.

#. Login to Karaage as administrator.
#. Select ``machines`` in the menu on the left.
#. Select ``Add machine category`` in the action bar.
#. Type in the name and select a datastore.
#. Select save.

.. index:: pair: machine; adding

Adding a Machine
================

You can add a :term:`machine` to a :term:`machine category`.

#. Login to Karaage as administrator.
#. Select ``machines`` in the menu on the left.
#. Select ``Add machine`` in the action bar.
#. After creating the machine, you may need to assign it a a password. Click
   the password button to generate a new password automatically.
#. If/when setting up django-pbs-logger, make sure if connects to Karaage
   using the machine name and the password you were given above.
