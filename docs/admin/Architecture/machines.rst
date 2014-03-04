Machines
========

This application defines clusters and cluster accounts.

Machine
-------

Defines a cluster, how many cpus and the start and end date of the
cluster. This is used to determine the total available hours when
compiling usage information.

MachineCategory
---------------

A MachineCategory is a group of Machines that share the same user
account backend. (eg. they all use the same LDAP server)

UserAccount
-----------

A UserAccount links a Person with a MachineCategory.
