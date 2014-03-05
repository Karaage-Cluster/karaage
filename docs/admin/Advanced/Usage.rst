Collecting usage statistics
===========================

How it works
------------

You can send usage logs to Karaage via xmlrpc. The xmlrpc interface is
located at / kg-manage shell from django.contrib.auth.models import
User, Permission user = User.objects.create\_user('usage-logger', '',
'') permission = Permission.objects.get(codename='change\_project')
permission.user\_set.add(user)

Install usage logger on cluster
-------------------------------

PBS/Torque
~~~~~~~~~~

Install :doc:`/Installing/karaage-pbs-logger`

Others
~~~~~~

There is also support for SGE and Slurm but no native packages as yet.
