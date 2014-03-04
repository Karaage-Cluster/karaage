Features
========

Roles
-----

Karaage has several roles

Users
-----

-  Allow users to:
-  Modify their own account
-  Change password
-  Manage what projects they are in
-  Join or create new projects

Project Managers
----------------

-  Allow project managers to:
-  Approve/Decline applications to join their project.
-  Reset passwords for their members.
-  Track their resource utilisation and software utilisation

Institute Delegates
-------------------

An Institute is just a group of projects.

-  Allow institute delegates to:
-  Approve/Decline new project applications.
-  Manage all projects and users under the institute.

Staff
-----

-  Can log into the Karaage Admin site.
-  See information about all
   users/projects/institutes/applications/usage etc.
-  Can be given permissions to ad/edit/delete users/projects/institutes
   etc.

Karaage Superusers
------------------

-  Can do anything

Usage Reporting
---------------

-  Report on a per institute, per project or per user for CPU usage
-  Track usage of software and versions
-  Keep track of what software (and version) and type of jobs a user is
   running

Karaage Admin
-------------

The interface is intended to be used by site admins only

Karaage Registration
--------------------

This site is intended to be used by end users of your systems.

It allows logged in users to

-  Edit their profile
-  Change their password
-  Accept software licenses for restricted software
-  Change their default project
-  Apply to join existing projects
-  Apply to start a new project

Unauthenticated users can apply for accounts and projects if this
feature is enabled

To enable registrations add the following to
/etc/karaage/registration\_settings.py

::

    ALLOW_REGISTRATIONS = True

By default usage information is private and only available to people who
are in the project

To allow anyone to view usage information add the following to
/etc/karaage/registration\_settings.py

::

    USAGE_IS_PUBLIC = True

