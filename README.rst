Karaage 3
=========

**Cluster account management tool.**

.. contents :: Table of Contents


What is Karaage?
----------------
Karaage is a cluster account management tool. It can manage users and projects
in a cluster and can store the data in various backends.


Features
--------
* Can store user information and/or posix account information in LDAP/Active Directory/passwd file.
* Email notifications.
* Auto account creation - Allow project leaders to manage their users.
* Applications work flow - Users can apply for accounts and be approved by project leaders.
* Usage reporting. Report on a per institute, per project or per user for CPU usage.
* Track usage of software and versions. Keep track of what software (and version) and type of jobs a user is running.


Documentation
-------------

- `Karaage 3.x User documentation
  <https://karaage.readthedocs.org/projects/karaage-user/en/latest/>`_

- `Karaage 3.x Programmer documentation:
  <https://karaage.readthedocs.org/projects/karaage-programmer/en/latest/>`_

- `Karaage 3.x Admin documentation: <https://karaage.readthedocs.org/en/latest/>`_


Components
----------

Karaage is a complicated application and has more then one source repository:

- `Karaage 3 karaage-cluster-tools
  <https://github.com/Karaage-Cluster/karaage-cluster-tools>`_
- `TLDAP library
  <https://github.com/Karaage-Cluster/python-tldap>`_
- `ALogger library
  <https://github.com/Karaage-Cluster/python-alogger>`_
- `Website
  <https://github.com/Karaage-Cluster/Karaage-Cluster.github.io>`_
- `Slurm Docker packaging
  <https://github.com/Karaage-Cluster/slurm>`_

Anything else not in this list has not been touched in years, and may not
be still relevant.


Plugins
-------

* karaage-usage: The karaage-usage plugin provides monitoring of usage
  information.
* karaage-applications: This plugin allows users to self register accounts with
  Karaage.
* karaage-software: Keep track of installed software applications.


Support
-------

* `Mailing list <https://groups.google.com/d/forum/karaage-users>`_
* `Bug reports <https://github.com/Karaage-Cluster/karaage/issues>`_


Source code
-----------
Karaage is open source code and available under the GPL3 license.  You can find
the source code for Karaage at `github <https://github.com/Karaage-Cluster/karaage/>`_.
