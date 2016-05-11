Release 3.1.28 (11 May 2016)
============================

* Ensure version.py gets installed.
* Ensure logout works with shibboleth.


Release 3.1.27 (10 May 2016)
============================

* Update programmer's documentation.
* Remove references to legacy documentation.
* Automatically fill username from shibboleth if we can.
* Various fixes for shibboleth work flow.
* Tests for login/logout.
* Display Karaage version in footnote.


Release 3.1.26 (06 May 2016)
============================

* Add shibboleth Apache configuration.
* Fix various shibboleth problems.
* Update shibboleth to use /Shibboleth.sso/Login instead of
  /Shibboleth.sso/DS.
* Display request.META values in SAML profile page.
* Fix render_link with latest Django Tables 1.2.0.
* Make first name and last name optional in shibboleth.
* Auto populate project application with email from shibboleth if possible.
* Redirect unknown shibboleth user to project application.
* Remove confusing shibboleth register button in application process.
* Make shibboleth login default in shibboleth enabled.
* Updates to programmer's documentation.


Release 3.1.25 (03 May 2016)
============================

* Move karaage.common.logging to common.logging, as we cannot initialize
  karaage.common at time logging is loaded with Django 1.9. Will require config
  change.


Release 3.1.24 (03 May 2016)
============================

* Updates to packaging.
* Updates to documentation.
* Fix tests for django_tables 1.2.0.
* Enable travis tests.


Release 3.1.23 (29 Apr 2016)
============================

* Fix tests and ensure everything still works.


Release 3.1.22 (19 Jun 2015)
============================

* Documentation updates.


Release 3.1.21 (17 Jun 2015)
============================

* Fix broken people list links.
* Fix Jessie references in documentation.
* Enhance unlock_training_account function.
* Add documentation on making new Karaage releases.


Release 3.1.20 (05 Jun 2015)
============================

* Override admin email addresses using APPROVE_ACCOUNTS_EMAIL setting.
* Fix flake8 tests in migrations.
* Change order of deactivate() function to avoid multiple updates to
accounts.
* Fix issues with MAM datastore.
* Sort applications in admin list by reverse expiry date by default.
* Display machine_category in account lists.
* Don't allow editing project leaders through edit view.
* Don't allow revoking last project leader.
* Add new ALLOW_NEW_PROJECTS setting, if set to False user's will not be
able to apply for new projects, only existing projects.


Release 3.1.19 (29 May 2015)
============================

* Numerous bug fixes.
* Display software stats correctly.
* Update documentation for Jessie.
* Update MAM and slurm documentation.
* Fix problems with latest slurm.
* Fix institute form.
* Support undelete project button.
* Fix display of leaders in bounce list.
* Set date_approved in approved applicants.
* Add more tests.
* Add HSTS to instruction.
* Change name of "Is existing person" button to "Mark duplicate user".
* Attempt to clarify emails.
* Add work around for ds389 bug. Note this won't work when adding a person
and setting their password at the same time; in this case please manually
reset the password to get it to work.
https://bugzilla.redhat.com/show_bug.cgi?id=1171308


Release 3.1.18 (13 Apr 2015)
============================

* Django 1.8 and 1.9 fixes.
  * Minor Schema change to last_login field of Person and Machine.
  * Email length in Person increased.
  * Fix RelatedObject related issues in Applications.
  * Plus others.
* Fix bug in software application listing.
* Fix incorrect name of query and jquery-ui files.


Release 3.1.17 (30 Mar 2015)
============================

* Cleanup code.
* Clanup css files and remove unused selectors.
* Support latest factory-boy.


Release 3.1.16 (17 Mar 2015)

* Generate error if alogger does not supply project in usage.
* Rebuild static files when upgrading package.
* Extend application expiry after it is approved.
* Allow resetting password even if no password set.
* Django 1.6 support was broken in 3.1.15, now fixed.
* Fix default URLs.
* Simplify autoconfiguration of plugins.


Release 3.1.15 (10 Mar 2015)
============================

* Various bug fixes.
* Simplification of code, mainly alogger and tests.


Release 3.1.14 (19 Feb 2015)
============================

* Add missing depends.
* Fix errors in installation documentation.
* Add untested Active Directory schema support.


Release 3.1.13 (17 Feb 2015)
============================

* Fix package cleanup.
* Ensure config file not world readable.


Release 3.1.12 (16 Feb 2015)
============================

* New upstream release.
* Move plugins to karaage.plugins.
* Various minor bug fixes.


Release 3.1.11 (12 Feb 2015)
============================

* Merge plugins into one source.
* Merge kgapplications and kgsoftware into karaage package.


Release 3.1.10 (01 Dec 2014)
============================

* Bug fixes.
* Fix problems with django-pipeline 1.4.0.
* Updates to documentation.


Release 3.1.9 (30 Oct 2014)
===========================

* Documentation: update apache configuration.
* Python3 fixes.
* UTF8 related fixes.
* Updates to upgrade documentation.


Release 3.1.8 (13 Oct 2014)
===========================

* Fix daily cleanup. Work properly with plugins.
* Test daily cleanup.


Release 3.1.7 (10 Oct 2014)
===========================

* Fix various MAM issues.
* Support MAM 2.7.


Release 3.1.6 (30 Sep 2014)
===========================

* More Django 1.7 updates.
* Django 1.6 should continue to work. For now.
* migrate_ldap always creates global DN in ldap if required.
* Fix problems with logentry migrations.


Release 3.1.5 (18 Sep 2014)
===========================

* Fix karaage3-database upgrade.
* Make work with Django 1.7
* Fix crash if no defined HTTP session with Django 1.6.
* We should fully support Django 1.7 now.


Release 3.1.4 (15 Sep 2014)
===========================

* Updates to fix Django 1.7 issues.
* Django 1.7 should really work now, however upgrade from earlier versions
not yet documented.


Release 3.1.3 (09 Sep 2014)
===========================

* Rewrite migrate_ldap.
* Add Django 1.7 migration.
* Documentation updates.
* New kg-migrate-south command.
* Django 1.7 should work, however not yet recommended for production use.


Release 3.1.2 (27 Aug 2014)
===========================

* Remove odd,even row classes.
* Fix broken templates.
* Move emails template directories.
* Move people template directories.
* Move machines template directories
* Move project template directories
* Move institutes template directories.
* Move common template directories
* Ensure migrate_ldap works properly with groups.
* Fix display of institute in migration.


Release 3.1.1 (19 Aug 2014)
============================

* Update documentation.
* Fix formatting.
* djcelery kludge.
* Split software out into plugin in karaagee-usage.
* Fix copyright.
* Use roles in applications.
* Fix project application specific wording.
* Make sure we include *.json files.
* Fix faulty role checks.
* Remove Django South hack.
* Make sure we kill the LDAP server after test fails.
* Fix migration errors.
* Turn karaage into one Django app.
* Fix management commands.
* Split applications into kgapplications.
* Update documentation.
* Fix migration issues.
* libapache2-mod-wsgi-py3 should be sufficient.
* Remove python2 specific use of iteritems.
* Remove software specific datastores.
* Combine templates.
* Cleanup links.
* Fix release tag.


Release 3.1.0 (30 Jul 2014)
============================

[ Brian May ]
* Update software usage statistics.
* Per institute software usage statistics.
* Verbose logging when creating application accounts
* Change link expiry text in emails.

[ Andrew Spiers ]
* Fix typo in kg-daily-cleanup.rst

[ Brian May ]
* userPassword should be text, not binary.
* Fix strings for Python 3.2.
* Make all strings in migrations "normal" strings.
* Fix migrate_ldap operation.
* Fix PEP8 issues.
* Fix Python 3 compatibility issues.
* Fix __unicode__ methods for Python 3.
* Python 3 tests.
* Python3 tracing change.
* Disable usage / south stuff if not available.
* Fix *all* PEP8 issues.
* More Python3 syntax errors fixed.
* Fix double quoted strings in migrations.
* Remove depreciated warnings.
* Fix Python3 PEP8 errors.
* Recommend mysql.connector.django over mysqldb.
* Redo Debian packaging.
* Support TLDAP 0.3.3
* Rename global_settings.py to settings.py
* Copy and adapt file from django-xmlrpc.
* Fix copyright declaration.
* Declare Python 3 compatible.
* Split usage stuff into kgusage.
* Fix Debian packaging issues.
* Update documentation.
* Update plugin API.
* Fix directory name in comment.
* Change permissions for all of /var/cache/karaage3.
* Don't run migrations unless Karaage is configured.
* More changes to plugin API.
* Add missing dpkg triggers.
* Conceal stderr output from init.d script.
* Apache2.2 and 2.4 autoconfiguration.
* Depend on apache2.
* Don't import debconf everywhere.
* Simplify apache2.2 config.
* Rename check() to check_valid().
* karaage3-apache supercedes old packages.
* Disable django-south if not available.
* Silence Django 1.7 upgrade warnings.
* Add south to build depends.
* Fix XMLRPC and add tests.
* Remove legacy project_under_quota function.
* Update changelog.
* Add build depends on flake8.
* Fix lintian issues and other problems.
* Make tests optional.
* Combine apache config files into one.
* Rename karaage3-apache to karaage3-wsgi.
* Move non-py files to common package.
* Add lintian override for karaage3-wsgi.
* Add lintian overrides for karaage3-database.
* Modify Apache2.2 test.


Release 3.0.15 (17 Jun 2014)
============================

* Fix account detail page for admin.
* Change get_absolute_url for accounts.
* Paranoid security checks.
* Allow users to change default project.
* Remove depends on python.
* Ensure admin request emails have correct link.
* PEP8 improvement.
* Fix PEP8 issue in comment.
* Remove non-PEP8 compliant white space.
* Support searching multiple directories for gold.
* Display more project application details.


Release 3.0.14 (27 May 2014)
============================

* Put all tables inside table-container.
* Remove calc from css.
* Make headings more consistent.
* Update depends.
* Remove legacy stuff.
* Update LDAP documentation.
* Fix uninitialized is_admin value.
* Remove unneeded import.
* Ensure username is not included in the password.
* Revert "Use named URLs in get_email_link"
* Fix account permissions.


Release 3.0.13 (05 May 2014)
============================

* Specify python/debian mappings.
* Update migrations threshold.
* Remove duplicate active row.
* Fix incorrect link.
* Don't migrate if configure not called.
* Triggers for static files.


Release 3.0.12 (01 May 2014)
============================

[ Brian May ]
* Remove unused file.
* Fix PEP8 issues in initial config.
* Update jquery.
* Remove make_leader option from applicant from.
* Don't set make_leader to False for new projects.
* Display if this application has make_leader set.
* Use python-pipeline to compress css and js files.
* Fix display of icons.
* Remove Javascript global variables.
* New setting for debuging django-pipeline.
* Change commented out value of ALLOW_REGISTRATIONS.
* Create log files owned by www-data user.
* Fix: Include header message in invitation.
* Don't reset created_by on reopening application.
* Simplify invite process.
* Grant leader/revoke leader operations.

[ Kieran Spear ]
* Honour 'make_leader' for application approval

[ Brian May ]
* Use css style, instead of direct icon reference.
* Use django-filter and django-tables2 for people.
* Use django-filter and django-tables2 for institutes.
* Use django-filter and django-tables2 for projects.
* Use django-filter and django-tables2 for machines.
* Use django-filter/django-tables2 for applications.
* Use django-filter/django-tables2 for software.
* Use django-filter/django-tables2 for logs.
* Use django-filter/django-tables2 for usage.
* Remove obsolete cruft.
* Sort order of INSTALLED_APPS.
* Replace gen_table with django_tables.
* Use th instead of td for table headings.
* Show exta buttons for inactive people.
* datastores get_*_details don't error if not found.
* Remove legacy code; self._person is always defined.
* Remove legacy db table.
* Fix migration error.
* Active column for people.
* More work on active/status indication.
* Remove debugging.
* Simplify account display.
* Tidy code.
* Tweak filters.
* Improvements to pagination.
* Use correct format specifier for minutes.
* Show if person is admin or not in details page.


Release 3.0.11 (10 Apr 2014)
============================

[ Brian May ]
* Fix replaces/breaks headers.
* Test password reset procedure.
* Add documentation for CLI commands.
* Correct copyright statement.

[ Kieran Spear ]
* Use named URLs in get_email_link
* Don't hardcode login_url in login_required decorator

[ Brian May ]
* Fix migration errors during upgrades from 2.7.
* Update kgcreatesuperuser command:
* Use new TLDAP check_password method.
* Fix application errors selecting projects.
* Fix error saving group.
* Fix errors changing passwords.
* Test password change forms.
* Ensure errors are emailed.
* If applicant is admin let them edit application.
* Use autocomplete to select leader/project.
* Add "make leader" field to project select form.


Release 3.0.10 (02 Apr 2014)
============================

* Add migration to resize applicant.username.
* Fix typo in in 389 support.
* Update LDAP settings for latest TLDAP.
* Move kg-manage and kg-daily-cleanup from karaage-admin.
* Fix issue with datastore methods being called incorrectly.
* Validate group name for new institutes.
* Validate group name for new software.
* Update logging calls.


Release 3.0.9 (25 Mar 2014)
===========================

[ Russell Sim ]
* Increase max length of institute identifier to 255
* Increase max length of account username to 255
* Increase the max length of group name to 255
* Increase the max username length to 255
* Increase application username length to 255

[ Brian May ]
* Don't use shell=True
* Allow displaying of all errors.

[ Russell Sim ]
* Fixed bug with incorrect mixin declaration

[ Brian May ]
* Fix pep8 issues.
* Institute graphs report unused space
* Fix undefined variables.
* Add test to change group in related objects.

[ Russell Sim ]
* Fix failure when using cracklib
* Moved test packages out of the install section
* Added unit test base class
* Better testing of institutional group changes
* New logging API

[ Brian May ]
* Use python logging.
* Move project_trend_graph to projects directory.
* Fix PEP8 issues.
* Check if userapplication content type exists.
* Fix PEP8 issues.
* Add missing import.
* Fix PEP8 issues.
* Fix error referencing DoesNotExist.
* Add missing import.
* Fix PEP8 issues.
* Add missing import.
* Remove change_default_project xmlrpc function.
* Fix more pep8 issues.
* PEP8 fixes.
* More PEP8 fixes.
* PEP8 fixes.
* Fix PEP8 issues in migrations.
* PEP8 issue solved.
* PEP8 issue solved.
* Fix breakage introduced in PEP8 cleanup
* Use django's validate_email function.
* Update authors.

[ Russell Sim ]
* Fixed flake8 check
* Increase project pid to 255
* Better testing of project group changes


Release 3.0.8 (14 Mar 2014)
===========================

* Remove REMOTE_USER middleware from karaage.middleware.auth
Django now has django.contrib.auth.middleware.RemoteUserMiddleware
and django.contrib.auth.backends.RemoteUserBackend.
* Fix error in calling log function in Applications.
* Test changes in Karaage source code with flake8.


Release 3.0.7 (13 Mar 2014)
===========================

* Numerous fixes to logging.
* Fix password reset URL.
* Numerous errors fixed.
* Updates to documentation.
* Fix to SAML middleware.
* Fix account username validation.
* Fixes to renaming people and projects.
* Hide project edit button if not leader.


Release 3.0.6 (11 Mar 2014)
===========================

* Various bugs fixed.
* Update python packaging.
* Rename Debian packages to Debian python compliant names.
* Add legacy packages for backword compatibility.


Release 3.0.5 (03 Mar 2014)
===========================

* Start arranging code into correct modules.
* Display profile menu in top level profile page.
* Cosmetic changes.


Release 3.0.4 (27 Feb 2014)
===========================

* Redesign datastores.
* Some small config changes required. See /usr/share/doc/karaage3/NEWS.
* Bugs fixed.
* New theme.


Release 3.0.3 (24 Feb 2014)
===========================

* New release of Karaage.
* Updates to theme.
* Lots of bug fixes.
* Updates to documentation.
* Restructure the views.


Release 3.0.2 (05 Feb 2014)
===========================

* Bugs fixed.
* Update documentation.
* Updates to installation procedures.


Release 3.0.1 (30 Jan 2014)
===========================

* Various bugs fixed.
* Add unique constraints to usage caches.
* Usage uses django-celery.


Release 3.0.0 (18 Jul 2013)
===========================

* MAJOR CHANGES. BACKUP EVERYTHING ***BEFORE*** INSTALLING. BACKUP MYSQL.
BACKUP OPENLDAP. TEST YOU CAN USE RESTORE MYSQL AND OPENLDAP. TEST
MIGRATIONS WORK ON TEST SYSTEM WITH REAL DATA BEFORE INSTALLING ON
PRODUCTION BOX.  MIGRATIONS MAY TAKE SOME TIME TO COMPLETE ON REAL DATA
(ESPECIALLY IF CPUJob CONTAINS MANY ITEMS).
* Improved support for transactions.
* Various bugs fixed.
* Make mysql database authoritive over LDAP.
* Add is_locked field to Person and UserAccount.
* Add shell attribute to UserAccount.
* Add group model.
* Clean up data stores.
* Validate telephone numbers.
* Use dpkg triggers to migrate db changes.
* Update packaging.
* People don't have a LDAP entry unless they have an account.
* User's set password after account is created via password reset email.
* Use new methods stuff in tldap 0.2.7.
* We no longer require placard, change depends to depends on django-tldap.
* Remove project machine_category and machine_categories fields.
* Rename user fields to person.
* Rename ProjectCache.pid to ProjectCache.project
* Rename UserAccount to Account.
* Rename UserCache to PersonCache.
* Merge User db model/table into Person.
* For Project table, pid is no longer PK.
* Migrations for all of the above.
* Rewrite graphs.
* Existing LDAP entries for non-accounts will get deleted in db migration.
* URLS changed.
* Cleaned templates.
* Intergrate slurm/gold functionality as datastores.
* Simplify dependencies.
* Rewrite applications app.
* Anything not mentioned above was also changed.
* World peace is still to come.


Release 2.7.6 (27 Mar 2013)
===========================

* Fix authentication for user's without a cluster account.
* Fix account expiry process.


Release 2.7.5 (25 Mar 2013)
===========================

* Fix error creating new accounts.
* Reverse lock/unlock links when editing person.


Release 2.7.4 (22 Mar 2013)
===========================

* Fix software data stores.
* Fix various errors initializing data for new users.
* Fix error in pbsmoab if user could not be found.


Release 2.7.3 (15 Mar 2013)
===========================

* Don't support Python 2.5


Release 2.7.3 (15 Mar 2013)
===========================

* Simplify default arguments.
* Remove duplicate initialization of machinecategory.
* Fix broken link in institute_form.html
* Update wiki link.
* Use GET for search, not POST.
* Fix confusion between person and accounts.
* debian


Release 2.7.2 (19 Feb 2013)
===========================

* Tests all work now.


Release 2.7.1 (11 Feb 2013)
===========================

* Increase the version number in __init__.py.


Release 2.7.0 (11 Feb 2013)
===========================

* New version.
* Based on latest django-placard.
* Lots of changes to templates. Existing templates might not display
correctly.


Release 2.6.8 (19 Nov 2012)
===========================

* Fix error in template. Requires permissions to see </ul> end tag.


Release 2.6.7 (14 Nov 2012)
===========================

* Fix placard templates, accidentally broken in last release.


Release 2.6.6 (13 Nov 2012)
===========================

* Fix broken software email templates.
* Update loginShell form processing.
* Updates to django ajax selects stuff.


Release 2.6.5 (16 Oct 2012)
===========================

* Update for latest django-ajax-selects.
* Remove obsolete code.
* Convert everything to use Django staticfiles.
* Make telehone number required in applicant form.
* Additional email address checks.
* Support Django 1.4.
* See https://github.com/Karaage-Cluster/karaage/issues?milestone=2&state=closed
* django-ajax-selects update
* project description
* Non-privileged admins can edit machine category
* latest django-ajax-selects support
* link_software error when unicode
* Error when no shell on unlocking
* Convert media files to staticfiles


Release 2.6.4 (22 Mar 2012)
===========================

* See https://github.com/Karaage-Cluster/karaage/issues?milestone=5&state=closed
* Method to get a users projects via XML RPC
* Comments for Applications
* Don't allow people to join a project they are already a member of
* Project management as a project leader
* View pending project details before accepting
* Users stay in LDAP group when deleting project
* Set default project by webpage
* logging in takes you to home page
* application list doesn't display the application title
* Unlocking an account that is already unlocked
* Make default shell configurable
* Make bounced shell configurable
* Display application type in application table
* Multiple invitations to same email for same project
* Page 2 of applications on User site is Empty
* Project start date in form
* Deleted and Rejected applications
* Usage divide by zero issue
* Approve software request link doesn't show up
* SAML duplicate email error
* Spelling mistake.
* update project fails
* Machine Category usage cache errors


Release 2.6.3 (7 Feb 2012)
==========================

* Jobname for a CPU Job increased to 256 characters
* Fixed bug for trend graphs when institute name had a / in it
* Ensure locked users can't change login shell
* Add users title to ldap
* Make names of software packages unique
* Log when user details are changed
* Added debconf question for DB migrations
* Added password reset function
* Allow project leaders to invite users to their projects
* Allow users to change their default project
* Show change password view on profile page
* Added managment commands to lock/unlock training accounts


Release 2.6.2 (19 Oct 2011)
===========================

* Handle module strings with // as a separator
* More filtering on software list
* Ensure usage index page is only accessible if allowed
* Other minor bug fixes


Release 2.6.1 (30 Aug 2011)
===========================

* Fixed out by 1 error when calculating available cpus
* Added memory and core usage reports
* Fixed institute usage permission view
* More sensible redirect after accepting a license
* Added DB index to date field on CPUJob
* Fixed longstanding matplotlib project graph error


Release 2.6 (02 Aug 2011)
=========================

* Institutes now have 0 or many delegates, got rid of active/sub delegates
* Removed deprecated requests app
* Refactor Account datastores. Setting now stored in DB
* Archive applications
* Ability to add/edit machine categories
* Reverse order of applications in admin site
* Set DEFAULT_FROM_EMAIL to be equal to ACCOUNTS_EMAIL
* Added software field to CPUJob
* Added CPU Job detail and list pages
* Send admin notification for pending project applications too
* Ability for an admin to modify an applicant
* Only create a group for a software package if it's restricted or has a license
* New management command to change a users username
* Added software usage statistics views
* Removed is_expertise field from projects
* Made the Send Email function more generic


Release 2.5.17 (15 Jul 2011)
============================

* Workaround for long standing matplotlib bug. Don't error
if can't display graph
* Fixed another SAML_ID unique bug


Release 2.5.16 (27 Jun 2011)
============================

* Fixed instutute usage bug


Release 2.5.15 (14 Jun 2011)
============================

* Fixed bug in user invite email sending
* Fixed broken decline link in project applications
* Fixed bug in software detail template


Release 2.5.14 (10 Jun 2011)
============================

* Ability to view accepted licenses
* Fixed bug where utilisation only showed up after 2nd request
* Prevent saml_id and passwords from being edited in any forms
* Other minor bug fixes


Release 2.5.13 (03 Jun 2011)
============================

* Ensure SAML ID doesn't get set on new applications
* This fixes a serious bug


Release 2.5.12 (03 Jun 2011)
============================

* Project approved emails were going to the wrong place
* Log view for applications. Log against the parent Application model
* Add example setting for REGISTRATION_BASE_URL
* Minor bugs fixed


Release 2.5.11 (01 Jun 2011)
============================

* Ensure project PIDs and institute names don't clash
* Fixed bug in application invites
* Added Project decline functions
* Ensure institute name is unique. Ensure saml attributes are unique
* Have a variable for user site for url links in emails
* Refactored email templates. Use .example as suffixes


Release 2.5.10 (25 May 2011)
============================

* Fixed SAML entity ID bug when editing institutes
* Password encoding bug for AD fixed
* Project application workflows - Admin approval
* Admin context processor for pending app count
* Improvements in the institute form
* Ability to override UserApplicationForm


Release 2.5.9 (18 May 2011)
===========================

* Fixed bug in graph generation when usage is unknown.
* Fixed bug in application saml institute logic
* Show unknow usage if user or project is NULL


Release 2.5.8 (04 May 2011)
============================

* Show all unknow usage function
* Set defaults for PERSONAL_DATASTORE and ACCOUNT_DATASTORES
* Use one template file for account approvals.
* Minor bug fixes


Release 2.5.7 (30 Mar 2011)
===========================

* Project Caps, multiple caps allowed
* Got rid of need for unknown user and project for missing usage
* Added software datastore
* Fixed some LDAP caching issues
* Various bug fixes and RPM packaging improvements


Release 2.5.6 (09 Mar 2011)
===========================

* Bug fixes
* Show saml ids in admin detail pages
* Changed create_password_hash to handle different formats


Release 2.5.5 (08 Mar 2011)
===========================

* Added initial code for SAML support
* Don't assume LDAP in kgcreateuser command
* Add CAPTCHA to application forms if in use


Release 2.5.4 (23 Feb 2011)
===========================

* Change default url for graphs to /karaage_graphs/
* Minor bug fixes


Release 2.5.3 (21 Feb 2011)
============================

* New application state ARCHIVE, handle multiple applications per applicant
* APPROVE_ACCOUNTS_EMAIL added
* Active Directory datastore
* Project applications
* Management command now deletes all applications that have been
complete for 30 days
* Ability to allow public access to usage information.
Default is to keep restricted
* Add CAPTCHA fields to application forms if no token and open
registrations allowed


Release 2.5.2 (15 Dec 2010)
===========================

* Add transaction middleware
* Force close LDAP connection to avoid stale data
* Update person when changing default project
* Update homeDir on account update
* friendlier message when application not in correct state
* Delete the applicant associated with application on deletion
* Added logging for application state changes


Release 2.5.1 (10 Dec 2010)
===========================

* Return distinct results in global search form
* Raise 403 error instead of 404 when application exists
but is in wrong state.
* Force user sync for LDAP on changing default project
* Show secret token in admin view
* Use model auth backend too to support alogger and the likes
* Use andsomes is_password_strong method instead of own


Release 2.5 (17 Nov 2010)
=========================

* Project Datastores
* Support for system users
* Machine scaling factor
* Handle Applications more generically and allow easier subclassing
* Institute datastores
* ProjectApplications
* Create default machine category when machines app is created
* Generate SECRET_KEY in new installations
* Many bug fixes throughout code


Release 2.4.14 (17 Nov 2010)
============================

* Added CSV user import command
* Ensure applicant with same email doesn't exist when inviting
* Minor bug fixes


Release 2.4.13 (20 Oct 2010)
============================

* Make sure invitation isn't expired
* Send different email if existing user on account creation
* Usage bug fixes
* allow admin to change application request options
* optional redirect after changing default project
* Ability to delete applications in admin view
* Spelling mistakes
* Other various bug fixes


Release 2.4.12 (13 Oct 2010)
============================

* Make header_message required field in application invite form
* Only show software that has a license for users to accept
* Bug fixes


Release 2.4.11 (07 Oct 2010)
============================

* Select related to lessen SQL queries
* Fixed bug in log parser if user has two accounts
* Allow existing users to apply for new projects
* Added project application form
* Ensure Applicant email is unique
* Changes to ProjectApplication model
* Display pending applications to project leaders in profile
* Allow project leader to select 'needs account'
* Pending applications for user plus decline applications
* Name of NEW state is Invitaion sent
* More explicit confirm when inviting users that already exist in system


Release 2.4.10 (04 Oct 2010)
============================

* Fixed serious cirular import bug


Release 2.4.9 (29 Sep 2010)
===========================

* New Application app
* Fixed bug in password done template
* Other minor fixes


Release 2.4.8 (15 Sep 2010)
===========================

* Added memory and core usage reports
* Use django-ajax-selects
* Use new messaging framework
* Ability to change is_staff and is_superuser
* Bug fixes and code cleanup


Release 2.4.7 (25 Aug 2010)
===========================

* Use django-andsome baseurl context
* Bug fixes


Release 2.4.6 (25 Aug 2010)
============================

* Added ability to request software.
* Cleaned up permission system on who can view what
* Moved project usage URL
* Bug fixes


Release 2.4.5 (17 Aug 2010)
===========================

* Use BigInteger field in usage fields
* Fix import error in request forms


Release 2.4.4 (12 Aug 2010)
===========================

* Set django password to unusable once user has password in ldap
* Removed required fields on most user form fields.
* Only able to change password if user is unlocked. Fixes #63
* Remove hardcoded link to VPAC usage graph.
* Other small bug fixes


Release 2.4.3 (28 Jul 2010)
===========================

* Make kgcreatesuperuser script smarter
* Don't error if graphs not implemented in specific library


Release 2.4.2 (28 Jul 2010)
===========================

* Dropped support for Django 1.1.1
* LOGIN_URL settings move to karaage-admin


Release 2.4.1 (27 Jul 2010)
===========================

* Added command to create a karaage superuser
* Make LDAP Auth backend the default
* If no logged in user log events under the new user
* Make country field optional on Person model


Release 2.4 (27 Jul 2010)
=========================

* Minor config changes
* Changes to default settings for new installs
* Bug fixes to project form


Release 2.3.11 (21 Jul 2010)
============================

* Compatible with Django 1.1
* Other tweaks to default configuration.
* Minor updates to configuration.
* Add script to set default secret.


Release 2.3.10 (20 Jul 2010)
============================

* Change to non-native format.
* Use new configuration system.
* Other improvements to packaging.


Release 2.3.9 (08 Jun 2010)
===========================

* Fixed syntax error


Release 2.3.8 (08 Jun 2010)
===========================

* Fixed Django 1.2 incompatibility


Release 2.3.7 (31 May 2010)
===========================

* Remove username from account creation form, fixes #43.
* Allow searching for project ID's in choose project that are longer that 8 characters


Release 2.3.6 (28 May 2010)
===========================

* Removed comment field from request detail
* Only activate a user if not already active


Release 2.3.5 (28 May 2010)
===========================

* Fix issue of not being able to search from page 2+ in userlist, Fixes #40
* Fixed #44 </tr> tag now in correct place for valid html
* Fixed bug in get_available_time and created a test to make sure it's correct
* Allow PID to be specified in admin project form
* More testing


Release 2.3.4 (26 May 2010)
===========================

* Decreased verbosity in management scripts
* Split user forms up one with username/password, one without
* Don't update datastore when saving a user in create script
* Only require required attributes in create_new_user method
* Moved to using django-simple-captcha instead of custom one
* Changed ordering when updating users in ldap datastore. Fixes #41
* More unit tests


Release 2.3.3 (19 May 2010)
===========================

* Gecos and gidNumber are now also configurable via ldap_attrs


Release 2.3.2 (19 May 2010)
===========================

* Pull in django-south dependency


Release 2.3.1 (19 May 2010)
===========================

* Use active institutes in forms


Release 2.3 (19 May 2010)
=========================

* Use Django-south for DB migrations
* Added is_active field to Institute


Release 2.2.1 (17 May 2010)
============================

* Fixed create_account bug with ldap_attrs


Release 2.2 (17 May 2010)
=========================

* Use dynamic values when creating an LDAP account. Also supply default_project when creating accounts
* Code clean up
* Added unittests for people and set up testing framework and project
* Bugfix for graphs when no machines
* Quota equals zero bug and signals to add IntituteChuck automatically
* Show jobID in default usage list.
* Added pylint file


Release 2.1.1 (07 May 2010)
===========================

* Ability to set LOCKED_SHELL. Fixes #34
* objectClass now configurable


Release 2.1 (06 May 2010)
=========================

* Changed size of cpu_job.jobname from 20 -> 100. REQUIRES DB change
* removed is_expertise from user project form
* By default expect a non expertise project when creating a project ID
* Removed VPAC in text on admin person form


Release 2.0.16 (05 May 2010)
============================

* Better way of checking to see if user is locked or not


Release 2.0.15 (05 May 2010)
============================

* Removed VPAC specific lock DN


Release 2.0.14 (03 May 2010)
============================

* Fixed usage bug when no projectchunk
* Fixed JS broken link on project form


Release 2.0.13 (03 May 2010)
============================

* Added initial data for default MachineCategory. Fixes #31
* Added initial api docs
* Added some management commands for clearing and populating
usage cache and locking expired users
* Don't display title if it doesn't exist. Fixes #30


Release 2.0.12 (29 Apr 2010)
============================

* Attempts to fix usage error. addresses #25


Release 2.0.11 (28 Apr 2010)
============================

* Fixed broken graph urls


Release 2.0.10 (28 Apr 2010)
============================

* Provide GRAPH_URL in template context


Release 2.0.9 (28 Apr 2010)
===========================

* GRAPH_URL and GRAPH_ROOT settings if graph dir separate to MEDIA_*


Release 2.0.8 (01 Apr 2010)
===========================

* Fixed software_detail bug


Release 2.0.7 (31 Mar 2010)
===========================

* Fixed totals displaying in usage_institute_detail page
* Use new django aggregation support instead of raw sql
* Show project usage based on machine_category


Release 2.0.6 (24 Mar 2010)
===========================

* Fixed bug in project reports url redirection


Release 2.0.5 (22 Mar 2010)
===========================

* Depend on django-xmlrpc package


Release 2.0.4 (22 Mar 2010)
===========================

* Actually use new alogger library


Release 2.0.3 (22 Mar 2010)
===========================

* Depend on python-alogger


Release 2.0.2 (19 Mar 2010)
===========================

* Fixed gdchart2 requirment


Release 2.0.1 (19 Mar 2010)
===========================

* Initial release.
