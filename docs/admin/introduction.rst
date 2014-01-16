Introduction
============

What is Karaage?
----------------
Karaage is a cluster account management tool. It can manage users and projects in a cluster and can store the data in various backends.

Terminology
-----------

person
  A person who has access to the karaage-registration system. A person could have one/more accounts,
  be an administrator, be a project manager, be an institute delegate. These are optional.

machine
  A single cluster or computer which is managed as a distinct unit.

machine category
  A group of machines that share the same authentication systems.

data store
  A list of external databases that we should link to and update automatically.
  Supported databases include LDAP, Gold, and Slurm.

account
  A person may have one or more accounts. An account allows a person to access
  machines on a given machine_category.

group
  A list of people. Usually maps directly to an LDAP Group, but this depends on the data stores used.

project
  A list of people who share the common goal.

project manager
  A person who manages a project, and can allow new user's to use the project.

institute
  An Institute is just a group of projects.

institute delegate
  A person who manages an institute, and can allow new project's for the institute.

administrator
  A person who has administration rights and can access karaage-admin.


Features
--------
* Can store user information and/or posix account information in LDAP/Active Directory/passwd file.
* Email notifications.
* Auto account creation - Allow project leaders to manager their users.
* Applications work flow - Users can apply for accounts and be approved by project leaders.
* Usage reporting. Report on a per institute, per project or per user for CPU usage.
* Track usage of software and versions. Keep track of what software (and version) and type of jobs a user is running.


karaage-admin
-------------
Admin portal for cluster administrators (karaage-admin).

* See/modify information about all users/projects/institutes/applications/usage etc.
* Many changes are logged.

karaage-registration
--------------------
User portal for cluster account holders (karaage-registration).

Allows users to:

* Modify their own account.
* Change password.
* Manage what projects they are in.

Allow project managers to:

* Approve/Decline applications to join their project.
* Reset passwords for their members.
* Track their resource utilisation and software utilisation.

Allow institute delegates to:

* Approve/Decline new project applications.
* Manage all projects and users under the institute.
