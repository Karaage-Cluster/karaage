Introduction
============

What is Karaage?
----------------
Karaage is a cluster account management tool. It can manage users and projects in a cluster and can store the data in various backends.

Terminology
-----------

:index:`person <person;definition>`
  A person who has access to the Karaage system. A person could have one/more
  accounts, be an administrator, be a project leader, be an institute
  delegate. These are optional.

:index:`machine <machine;definition>`
  A single cluster or computer which is managed as a distinct unit.

:index:`machine category <machine category;definition>`
  A group of machines that share the same authentication systems.

:index:`data store <data store;definition>`
  A list of external databases that we should link to and update automatically.
  Supported databases include LDAP, Gold, and Slurm.

:index:`account <account;definition>`
  A person may have one or more accounts. An account allows a person to access
  machines on a given machine_category.

:index:`group <group;definition>`
  A list of people. Usually maps directly to an LDAP Group, but this depends on the data stores used.

:index:`project <project;definition>`
  A list of people who share the common goal.

:index:`project leader <project leader;definition>`
  A person who manages a project, and can allow new user's to use the project.

:index:`institute <institute;definition>`
  An Institute is just a group of projects.

:index:`institute delegate <institute delegate;definition>`
  A person who manages an institute, and can allow new project's for the institute.

:index:`administrator <administrator;definition>`
  A person who has administration rights and can access karaage-admin.


.. index:: Karaage; features

Features
--------
* Can store user information and/or posix account information in LDAP/Active Directory/passwd file.
* Email notifications.
* Auto account creation - Allow project leaders to manager their users.
* Applications work flow - Users can apply for accounts and be approved by project leaders.
* Usage reporting. Report on a per institute, per project or per user for CPU usage.
* Track usage of software and versions. Keep track of what software (and version) and type of jobs a user is running.

.. index:: Karaage; Karaage-admin

karaage-admin
-------------
Admin portal for cluster administrators (karaage-admin).

* See/modify information about all users/projects/institutes/applications/usage etc.
* Many changes are logged.

.. index:: Karaage; Karaage-registration

karaage-registration
--------------------
User portal for cluster account holders (karaage-registration).

Allows users to:

* Modify their own account.
* Change password.
* Manage what projects they are in.

Allow project leaders to:

* Approve/Decline applications to join their project.
* Reset passwords for their members.
* Track their resource utilisation and software utilisation.

Allow institute delegates to:

* Approve/Decline new project applications.
* Manage all projects and users under the institute.
