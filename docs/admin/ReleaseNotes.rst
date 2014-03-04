Release Notes
=============

These are the release notes for the karaage package. This only lists
major changes. For more details, see one of:

-  `karaage
   changelog <https://github.com/Karaage-Cluster/karaage/blob/master/debian/changelog>`_.
-  `karaage-admin
   changelog <https://github.com/Karaage-Cluster/karaage-admin/blob/master/debian/changelog>`_.
-  `karaage-registration
   changelog <https://github.com/Karaage-Cluster/karaage-registration/blob/master/debian/changelog>`_.

3.0.0
-----

This has numerous changes. Some of the highlights:

-  Should be considered alpha quality. Should be working, however some
   things might change.
-  Mysql database authoritative over LDAP. That is if anything else
   changes your LDAP server, these changes might get lost under certain
   circumstances. This has not changed.
-  Clean up SQL schemas.
-  Add group model.
-  Clean up data stores.
-  Use dpkg triggers to migrate db changes.
-  People don't have a LDAP entry unless they have an account.
-  User's set password after after their account is created.
-  We no longer require placard, change depends to depends on
   django-tldap.
-  We no longer require django-andsome, was merged into karaage package.
-  We no longer require karaage-common, was merged into karaage package.
-  Existing LDAP entries for non-accounts will get deleted in db
   migration.
-  Changes to schema that may break existing code and/or templates.
-  gold/slurm code moved from kglimits into karaage/datastores, and
   needs configuration.

Do not use for production systems. However, please do test Karaage
3.0.0. Copy your mysql and openldap databases and make sure everything
works, including the migrations.

2.7.0
-----

-  Significant changes to templates.
-  Use new tldap library.
-  Requires latest django-placard.

2.6.5
-----

-  Project taken over by Brian May
-  Update for latest django-ajax-selects.
-  Remove obsolete code.
-  Convert everything to use Django staticfiles.
-  Make telehone number required in applicant form.
-  Additional email address checks.
-  Support Django 1.4.
-  See
   https://github.com/Karaage-Cluster/karaage/issues?milestone=2&state=closed

   -  django-ajax-selects update
   -  project description
   -  Non-privileged admins can edit machine category
   -  latest django-ajax-selects support
   -  link\_software error when unicode
   -  Error when no shell on unlocking
   -  Convert media files to staticfiles

2.6.0
-----

-  Institutes now have 0 or many delegates, got rid of active/sub
   delegates You can choose who receives email notifications.
-  Removed deprecated requests app
-  Ability to archive applications. Archived applications will never be
   deleted. Completed applications will be deleted 1 month from going to
   completed state.
-  Ability to add/edit machine categories
-  Refactor Account datastores. Setting now stored in DB
-  Reverse order of applications in admin site
-  Ability to view all jobs and filter by project/user etc.
-  Send admin notification for pending project applications too.
   Previously only new user applications would trigger a notification.
-  Ability for an admin to modify an applicant during application
   process.
-  Only create a group for a software package if it's restricted or has
   a license
-  New management command to change a users username. See
   [wiki:Advanced/ManagementCommands#change\_username
   ManagementCommands]
-  New software usage reporting. Have the ability to report on software
   used. See [[SoftwareReporting\|Advanced/SoftwareReporting]]
-  Removed is\_expertise field from projects
-  New Send Email functionality in Admin. Can send emails to all users,
   all leaders and all users with a cluster account.

2.5.7
-----

-  Got rid of need for unknown user and project for missing usage
-  No longer need to create LDAP groups for each software package. This
   is done automatically now.

2.5.0
-----

-  More automation when installing karaage the 1st time
-  Project and Institute Datastores - see [[Advanced/DataStores]]
-  Ability to mark a user as a system user - Useful for non human people
   in karaage
-  Machine scaling factor when calculating usage
-  Project Applications
-  Lots of bug fixes

