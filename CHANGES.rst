==========
Change log
==========
All notable changes to this project will be documented in this file. The format
is based on `Keep a Changelog`_ and this project
adheres to `Semantic Versioning`_.

.. _`Keep a Changelog`: http://keepachangelog.com/
.. _`Semantic Versioning`: http://semver.org/


5.0.11 (2019-02-20)
-------------------

Changed
~~~~~~~
* Update gunicorn from 19.8.1 to 19.9.0.
* Update reportlab from 3.5.8 to 3.5.9.
* Update sphinx from 1.8.1 to 1.8.2.
* Remove legacy LDAP classes.
* Update to latest python-tldap.
* Update supported Python versions to 3.6 and 3.7 only.
* Attempt to fix travis db issues.
* Update Django for Python 3.7 support.
* Update HOME_DIRECTORY format specification.
* Remove legacy locked shell stuff.
* Remove legacy home directory setting code.
* Remove legacy test settings.

Fixed
~~~~~
* Correctly show group name in verbose view.


5.0.10 (2018-10-04)
-------------------

Changed
~~~~~~~
* Update reportlab from 3.5.2 to 3.5.8.
* Update matplotlib from 2.2.2 to 2.2.3.
* Update whitenoise from 3.3.1 to 4.1.
* Update reportlab from 3.5.4 to 3.5.5.
* Update Django to latest in LTS series.
* Update sphinx from 1.7.6 to 1.8.1.
* Update reportlab from 3.5.5 to 3.5.6.
* Update django-ajax-selects from 1.7.0 to 1.7.1.
* Update django-extensions from 2.1.0 to 2.1.3.
* Update sphinx from 1.7.7 to 1.7.8.

Fixed
~~~~~
* Fix crash when saving extension. Fixes #476.


5.0.9 (2018-08-03)
------------------

Changed
~~~~~~~
* Update django-environ from 0.4.4 to 0.4.5.
* Update mysqlclient from 1.3.12 to 1.3.13.
* Update billiard from 3.5.0.3 to 3.5.0.4.
* Update reportlab from 3.4.0 to 3.5.0.
* Update django-filter from 1.1.0 to 2.0.0.
* Update sphinx from 1.7.5 to 1.7.6.
* Update django-extensions from 2.0.7 to 2.1.0.
* Update reportlab from 3.5.0 to 3.5.1.
* Update celery from 4.2.0 to 4.2.1.
* Update reportlab from 3.5.1 to 3.5.2.
* Update pyasn1 from 0.4.3 to 0.4.4.

Fixed
~~~~~
* Fix various issues creating new project application. Fixes #450.
* In application process don't list similar people or "Mark duplicate user"
  button unless user has approval rights.
* Rename "Mark duplicate user" button to "Mark duplicate person".
* Rename "Existing Project Details" to "Join Existing Project Details".


5.0.8 (2018-06-22)
------------------

Changed
~~~~~~~
* Update kombu from 4.2.0 to 4.2.1.
* Don't email project leaders with email turned off, but allow them to approve
  projects.
* Update celery from 4.1.1 to 4.2.0.
* Update django-simple-captcha from 0.5.7 to 0.5.9.


5.0.7 (2018-05-29)
------------------

Changed
~~~~~~~
* Remove amqp library requirement.
* Fixup slurm directory in documentation.
* Ensure /var/log/shibboleth has correct permissions.
* Update sphinx from 1.7.4 to 1.7.5.


5.0.6 (2018-05-25)
------------------

Changed
~~~~~~~
* Update sphinx from 1.7.3 to 1.7.4
* Update gunicorn from 19.7.1 to 19.8.0
* Remove legacy dockerhub hooks
* Update gunicorn from 19.8.0 to 19.8.1
* Added invite_csv_users.py for cli bulk inviting (#431)
* Update factory-boy from 2.10.0 to 2.11.1
* Update django-model-utils from 3.1.1 to 3.1.2
* Completely revise application process
* Allow institute delegates with emails turned off to approve applications
* Auto build beta docker image
* Update django-simple-captcha from 0.5.6 to 0.5.7
* Update kombu from 4.1.0 to 4.2.0
* Update celery from 4.1.0 to 4.1.1
* Update for latest slurm images
* Move dynamic files from /var/cache/karaage3/files to /var/lib/karaage3/files
* Update docker start instructions
* Update pyasn1 from 0.4.2 to 0.4.3

Removed
~~~~~~~
* Dropped support for slurm 16.02


5.0.5 (2018-04-26)
------------------

Fixed
~~~~~
* Fixed setup.py error.


5.0.4 (2018-04-24)
------------------

Changed
~~~~~~~
* Add ability to change default slurm add account command.


5.0.3 - 2018-04-23
------------------

Fixed
~~~~~
* Moved institute help text out of migration so it doesn't trigger a new
  migration when the email address changes.

Changed
~~~~~~~
* Fix out-by-one error in changelog versions.
* Improvements to static checks.
* Fix deprecation warnings.
* Update django-extensions from 2.0.0 to 2.0.2.
* Update matplotlib from 2.1.2 to 2.2.0.
* Update Django.
* Various updates to documentation.
* More work with tests.
* Update django-extensions from 2.0.2 to 2.0.7.
* Update django-tables2 from 1.19.0 to 1.21.2.
* Update ldap3 from 2.4.1 to 2.5.
* Update matplotlib from 2.2.0 to 2.2.2.
* Update sphinx from 1.7.1 to 1.7.3.


5.0.2 - 2018-02-28
------------------

Changed
~~~~~~~
* Update docker test scripts.
* Added reportlab to requirements for 3rd party plugin.

Fixed
~~~~~
* Deploy to dockerhub automatically on travis success.
* Fixed starting of celery process.


5.0.1 - 2018-02-20
------------------

Fixed
~~~~~
* Use text mode not binary when writing CSV files in usage.

Removed
-------
* Legacy south migrations.
* Legacy site creation.
* MachineCategories, ProjectQuotas, and InstituteQuotas.


3.1.34 - 2017-11-28
-------------------

Fixed
~~~~~
* Not updating passwords for datastores.
* Documentation issues.
* Don't log raw datastore password when changing password.
* Use novalidate for project selection form in application.


3.1.33 - 2017-11-02
-------------------

Fixed
~~~~~
* Do not send emails to locked or system accounts.


3.1.32 - 2017-11-17
-------------------

Added
~~~~~
* Docker support.

Changed
~~~~~~~
* Updated requirements.
* Python3.5 or Python3.6 required. Django 1.11 required.  Earlier versions will
  still work (for now) but are no longer tested.

Fixed
~~~~~
* E-Mail validation for admin person form.
* Fixed my email address.
* Various bugs fixed.

Removed
~~~~~~~
* Debian packages.


3.1.31 - 2017-05-03
-------------------

Changed
~~~~~~~
* Improve password fussiness.
* Find training accounts that are system users.
* TRAINING_ACCOUNT_PREFIX is now a regexp.

Fixed
~~~~~
* Applicants can have duplicate email and usernames.
* Various Django 1.10 fixes. Django >= 1.10 not yet supported.
* Improved error handling on approving applications.
* Update various dependencies, and fix related issues.
* Fix typo in emails. Administrator not Administrator.
* All tests pass under Django 1.10.
* Support tldap 1.4.1 and ldap3 2.2.3.
* Explicitly use bcrypt/pbkdf2_sha256 by default for passwords instead of SHA1.
  Update tests to use pbkdf2_sha256. Outside tests this was already the default
  with recent versions of Django.


3.1.30 - 2016-09-11
-------------------

* Fix various errors.
* Fix broken calls to render.
* Fix validation logic, licence details, new software.
* Save institute even if commit==False.


3.1.29 - 2016-08-11
-------------------

* Fix broken tests.
* Require at least one institute delegate.
* Make project leaders a required value.
* Don't crash if institute form invalid.
* Add mark_safe to required template tags.
* Strip leading and trailing space from input fields.
* Clarify purpose of Karaage password.
* Try to eliminate confusion in entering names.
* Make department field mandatory on applicant form.
* Update empty_text for similar_people_table.
* Don't output empty fields from Slurm.
* Requires Django >= 1.8
* Fix Django 1.10 compatibility warnings.


3.1.28 - 2016-05-11
-------------------

* Ensure version.py gets installed.
* Ensure logout works with shibboleth.


3.1.27 - 2016-05-10
-------------------

* Update programmer's documentation.
* Remove references to legacy documentation.
* Automatically fill username from shibboleth if we can.
* Various fixes for shibboleth work flow.
* Tests for login/logout.
* Display Karaage version in footnote.


3.1.26 - 2016-05-06
-------------------

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


3.1.25 - 2016-05-03
-------------------

* Move karaage.common.logging to common.logging, as we cannot initialize
  karaage.common at time logging is loaded with Django 1.9. Will require config
  change.


3.1.24 - 2016-05-03
-------------------

* Updates to packaging.
* Updates to documentation.
* Fix tests for django_tables 1.2.0.
* Enable travis tests.


3.1.23 - 2016-04-29
-------------------

* Fix tests and ensure everything still works.


3.1.22 - 2015-06-19
-------------------

* Documentation updates.


3.1.21 - 2015-06-17
-------------------

* Fix broken people list links.
* Fix Jessie references in documentation.
* Enhance unlock_training_account function.
* Add documentation on making new Karaage releases.


3.1.20 - 2015-06-05
-------------------

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


3.1.19 - 2015-05-29
-------------------

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


3.1.18 - 2015-04-13
-------------------

* Django 1.8 and 1.9 fixes.
  * Minor Schema change to last_login field of Person and Machine.
  * Email length in Person increased.
  * Fix RelatedObject related issues in Applications.
  * Plus others.
* Fix bug in software application listing.
* Fix incorrect name of query and jquery-ui files.


3.1.17 - 2015-03-30
-------------------

* Cleanup code.
* Clanup css files and remove unused selectors.
* Support latest factory-boy.


3.1.16 - 2015-03-17
-------------------

* Generate error if alogger does not supply project in usage.
* Rebuild static files when upgrading package.
* Extend application expiry after it is approved.
* Allow resetting password even if no password set.
* Django 1.6 support was broken in 3.1.15, now fixed.
* Fix default URLs.
* Simplify autoconfiguration of plugins.


3.1.15 - 2015-03-10
-------------------

* Various bug fixes.
* Simplification of code, mainly alogger and tests.


3.1.14 - 2015-02-19
-------------------

* Add missing depends.
* Fix errors in installation documentation.
* Add untested Active Directory schema support.


3.1.13 - 2015-02-17
-------------------

* Fix package cleanup.
* Ensure config file not world readable.


3.1.12 - 2015-02-16
-------------------

* New upstream release.
* Move plugins to karaage.plugins.
* Various minor bug fixes.


3.1.11 - 2015-02-12
-------------------

* Merge plugins into one source.
* Merge kgapplications and kgsoftware into karaage package.


3.1.10 - 2014-12-01
-------------------

* Bug fixes.
* Fix problems with django-pipeline 1.4.0.
* Updates to documentation.


3.1.9 - 2014-10-30
------------------

* Documentation: update apache configuration.
* Python3 fixes.
* UTF8 related fixes.
* Updates to upgrade documentation.


3.1.8 - 2014-10-13
------------------

* Fix daily cleanup. Work properly with plugins.
* Test daily cleanup.


3.1.7 - 2014-10-10
------------------

* Fix various MAM issues.
* Support MAM 2.7.


3.1.6 - 2014-09-30
------------------

* More Django 1.7 updates.
* Django 1.6 should continue to work. For now.
* migrate_ldap always creates global DN in ldap if required.
* Fix problems with logentry migrations.


3.1.5 - 2014-09-18
------------------

* Fix karaage3-database upgrade.
* Make work with Django 1.7
* Fix crash if no defined HTTP session with Django 1.6.
* We should fully support Django 1.7 now.


3.1.4 - 2014-09-15
------------------

* Updates to fix Django 1.7 issues.
* Django 1.7 should really work now, however upgrade from earlier versions
  not yet documented.


3.1.3 - 2014-09-09
------------------

* Rewrite migrate_ldap.
* Add Django 1.7 migration.
* Documentation updates.
* New kg-migrate-south command.
* Django 1.7 should work, however not yet recommended for production use.


3.1.2 - 2014-08-27
------------------

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


3.1.1 - 2014-08-19
------------------

* Update documentation.
* Fix formatting.
* djcelery kludge.
* Split software out into plugin in karaagee-usage.
* Fix copyright.
* Use roles in applications.
* Fix project application specific wording.
* Make sure we include ``*.json`` files.
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


3.1.0 - 2014-07-30
------------------

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


3.0.15 - 2014-06-17
-------------------

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


3.0.14 - 2014-05-27
-------------------

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


3.0.13 - 2014-05-05
-------------------

* Specify python/debian mappings.
* Update migrations threshold.
* Remove duplicate active row.
* Fix incorrect link.
* Don't migrate if configure not called.
* Triggers for static files.


3.0.12 - 2014-05-01
-------------------

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


3.0.11 - 2014-04-10
-------------------

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


3.0.10 - 2014-04-02
-------------------

* Add migration to resize applicant.username.
* Fix typo in in 389 support.
* Update LDAP settings for latest TLDAP.
* Move kg-manage and kg-daily-cleanup from karaage-admin.
* Fix issue with datastore methods being called incorrectly.
* Validate group name for new institutes.
* Validate group name for new software.
* Update logging calls.


3.0.9 - 2014-03-25
------------------

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


3.0.8 - 2014-03-14
------------------

* Remove REMOTE_USER middleware from karaage.middleware.auth
  Django now has django.contrib.auth.middleware.RemoteUserMiddleware
  and django.contrib.auth.backends.RemoteUserBackend.
* Fix error in calling log function in Applications.
* Test changes in Karaage source code with flake8.


3.0.7 - 2014-03-13
------------------

* Numerous fixes to logging.
* Fix password reset URL.
* Numerous errors fixed.
* Updates to documentation.
* Fix to SAML middleware.
* Fix account username validation.
* Fixes to renaming people and projects.
* Hide project edit button if not leader.


3.0.6 - 2014-03-11
------------------

* Various bugs fixed.
* Update python packaging.
* Rename Debian packages to Debian python compliant names.
* Add legacy packages for backword compatibility.


3.0.5 - 2014-03-03
------------------

* Start arranging code into correct modules.
* Display profile menu in top level profile page.
* Cosmetic changes.


3.0.4 - 2014-02-27
------------------

* Redesign datastores.
* Some small config changes required. See /usr/share/doc/karaage3/NEWS.
* Bugs fixed.
* New theme.


3.0.3 - 2014-02-24
------------------

* New release of Karaage.
* Updates to theme.
* Lots of bug fixes.
* Updates to documentation.
* Restructure the views.


3.0.2 - 2014-02-05
------------------

* Bugs fixed.
* Update documentation.
* Updates to installation procedures.


3.0.1 - 2014-01-30
------------------

* Various bugs fixed.
* Add unique constraints to usage caches.
* Usage uses django-celery.


3.0.0 - 2013-07-18
------------------

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


2.7.6 - 2013-03-27
------------------

* Fix authentication for user's without a cluster account.
* Fix account expiry process.


2.7.5 - 2013-03-25
------------------

* Fix error creating new accounts.
* Reverse lock/unlock links when editing person.


2.7.4 - 2013-03-22
------------------

* Fix software data stores.
* Fix various errors initializing data for new users.
* Fix error in pbsmoab if user could not be found.


2.7.3 - 2013-03-15
------------------

* Don't support Python 2.5


2.7.3 - 2013-03-15
------------------

* Simplify default arguments.
* Remove duplicate initialization of machinecategory.
* Fix broken link in institute_form.html
* Update wiki link.
* Use GET for search, not POST.
* Fix confusion between person and accounts.
* debian


2.7.2 - 2013-02-19
------------------

* Tests all work now.


2.7.1 - 2013-02-11
------------------

* Increase the version number in __init__.py.


2.7.0 - 2013-02-11
------------------

* New version.
* Based on latest django-placard.
* Lots of changes to templates. Existing templates might not display
  correctly.


2.6.8 - 2012-11-19
------------------

* Fix error in template. Requires permissions to see </ul> end tag.


2.6.7 - 2012-11-14
------------------

* Fix placard templates, accidentally broken in last release.


2.6.6 - 2012-11-13
------------------

* Fix broken software email templates.
* Update loginShell form processing.
* Updates to django ajax selects stuff.


2.6.5 - 2012-10-16
------------------

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


2.6.4 - 2012-03-22
------------------

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


2.6.3 - 2012-02-07
------------------

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


2.6.2 - 2011-10-19
------------------

* Handle module strings with // as a separator
* More filtering on software list
* Ensure usage index page is only accessible if allowed
* Other minor bug fixes


2.6.1 - 2011-08-30
------------------

* Fixed out by 1 error when calculating available cpus
* Added memory and core usage reports
* Fixed institute usage permission view
* More sensible redirect after accepting a license
* Added DB index to date field on CPUJob
* Fixed longstanding matplotlib project graph error


2.6 - 2011-08-02
----------------

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


2.5.17 - 2011-07-15
-------------------

* Workaround for long standing matplotlib bug. Don't error
  if can't display graph.
* Fixed another SAML_ID unique bug


2.5.16 - 2011-06-27
-------------------

* Fixed instutute usage bug


2.5.15 - 2011-06-14
-------------------

* Fixed bug in user invite email sending
* Fixed broken decline link in project applications
* Fixed bug in software detail template


2.5.14 - 2011-06-10
-------------------

* Ability to view accepted licenses
* Fixed bug where utilisation only showed up after 2nd request
* Prevent saml_id and passwords from being edited in any forms
* Other minor bug fixes


2.5.13 - 2011-06-03
-------------------

* Ensure SAML ID doesn't get set on new applications
* This fixes a serious bug


2.5.12 - 2011-06-03
-------------------

* Project approved emails were going to the wrong place
* Log view for applications. Log against the parent Application model
* Add example setting for REGISTRATION_BASE_URL
* Minor bugs fixed


2.5.11 - 2011-06-01
-------------------

* Ensure project PIDs and institute names don't clash
* Fixed bug in application invites
* Added Project decline functions
* Ensure institute name is unique. Ensure saml attributes are unique
* Have a variable for user site for url links in emails
* Refactored email templates. Use .example as suffixes


2.5.10 - 2011-05-25
-------------------

* Fixed SAML entity ID bug when editing institutes
* Password encoding bug for AD fixed
* Project application workflows - Admin approval
* Admin context processor for pending app count
* Improvements in the institute form
* Ability to override UserApplicationForm


2.5.9 - 2011-05-18
------------------

* Fixed bug in graph generation when usage is unknown.
* Fixed bug in application saml institute logic
* Show unknow usage if user or project is NULL


2.5.8 - 2011-05-04
------------------

* Show all unknow usage function
* Set defaults for PERSONAL_DATASTORE and ACCOUNT_DATASTORES
* Use one template file for account approvals.
* Minor bug fixes


2.5.7 - 2011-03-30
------------------

* Project Caps, multiple caps allowed
* Got rid of need for unknown user and project for missing usage
* Added software datastore
* Fixed some LDAP caching issues
* Various bug fixes and RPM packaging improvements


2.5.6 - 2011-03-09
------------------

* Bug fixes
* Show saml ids in admin detail pages
* Changed create_password_hash to handle different formats


2.5.5 - 2011-03-08
------------------

* Added initial code for SAML support
* Don't assume LDAP in kgcreateuser command
* Add CAPTCHA to application forms if in use


2.5.4 - 2011-02-23
------------------

* Change default url for graphs to /karaage_graphs/
* Minor bug fixes


2.5.3 - 2011-02-21
------------------

* New application state ARCHIVE, handle multiple applications per applicant
* APPROVE_ACCOUNTS_EMAIL added
* Active Directory datastore
* Project applications
* Management command now deletes all applications that have been
  complete for 30 days.
* Ability to allow public access to usage information.
  Default is to keep restricted.
* Add CAPTCHA fields to application forms if no token and open
  registrations allowed.


2.5.2 - 2010-12-15
------------------

* Add transaction middleware
* Force close LDAP connection to avoid stale data
* Update person when changing default project
* Update homeDir on account update
* friendlier message when application not in correct state
* Delete the applicant associated with application on deletion
* Added logging for application state changes


2.5.1 - 2010-12-10
------------------

* Return distinct results in global search form
* Raise 403 error instead of 404 when application exists
  but is in wrong state.
* Force user sync for LDAP on changing default project
* Show secret token in admin view
* Use model auth backend too to support alogger and the likes
* Use andsomes is_password_strong method instead of own


2.5 - 2010-11-17
----------------

* Project Datastores
* Support for system users
* Machine scaling factor
* Handle Applications more generically and allow easier subclassing
* Institute datastores
* ProjectApplications
* Create default machine category when machines app is created
* Generate SECRET_KEY in new installations
* Many bug fixes throughout code


2.4.14 - 2010-11-17
-------------------

* Added CSV user import command
* Ensure applicant with same email doesn't exist when inviting
* Minor bug fixes


2.4.13 - 2010-10-20
-------------------

* Make sure invitation isn't expired
* Send different email if existing user on account creation
* Usage bug fixes
* allow admin to change application request options
* optional redirect after changing default project
* Ability to delete applications in admin view
* Spelling mistakes
* Other various bug fixes


2.4.12 - 2010-10-13
-------------------

* Make header_message required field in application invite form
* Only show software that has a license for users to accept
* Bug fixes


2.4.11 - 2010-10-07
-------------------

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


2.4.10 - 2010-10-04
-------------------

* Fixed serious cirular import bug


2.4.9 - 2010-09-29
------------------

* New Application app
* Fixed bug in password done template
* Other minor fixes


2.4.8 - 2010-09-15
------------------

* Added memory and core usage reports
* Use django-ajax-selects
* Use new messaging framework
* Ability to change is_staff and is_superuser
* Bug fixes and code cleanup


2.4.7 - 2010-08-25
------------------

* Use django-andsome baseurl context
* Bug fixes


2.4.6 - 2010-08-25
------------------

* Added ability to request software.
* Cleaned up permission system on who can view what
* Moved project usage URL
* Bug fixes


2.4.5 - 2010-08-17
------------------

* Use BigInteger field in usage fields
* Fix import error in request forms


2.4.4 - 2010-08-12
------------------

* Set django password to unusable once user has password in ldap
* Removed required fields on most user form fields.
* Only able to change password if user is unlocked. Fixes #63
* Remove hardcoded link to VPAC usage graph.
* Other small bug fixes


2.4.3 - 2010-07-28
------------------

* Make kgcreatesuperuser script smarter
* Don't error if graphs not implemented in specific library


2.4.2 - 2010-07-28
------------------

* Dropped support for Django 1.1.1
* LOGIN_URL settings move to karaage-admin


2.4.1 - 2010-07-27
------------------

* Added command to create a karaage superuser
* Make LDAP Auth backend the default
* If no logged in user log events under the new user
* Make country field optional on Person model


2.4 - 2010-07-27
----------------

* Minor config changes
* Changes to default settings for new installs
* Bug fixes to project form


2.3.11 - 2010-07-21
-------------------

* Compatible with Django 1.1
* Other tweaks to default configuration.
* Minor updates to configuration.
* Add script to set default secret.


2.3.10 - 2010-07-20
-------------------

* Change to non-native format.
* Use new configuration system.
* Other improvements to packaging.


2.3.9 - 2010-06-08
------------------

* Fixed syntax error


2.3.8 - 2010-06-08
------------------

* Fixed Django 1.2 incompatibility


2.3.7 - 2010-05-31
------------------

* Remove username from account creation form, fixes #43.
* Allow searching for project ID's in choose project that are longer that 8 characters


2.3.6 - 2010-05-28
------------------

* Removed comment field from request detail
* Only activate a user if not already active


2.3.5 - 2010-05-28
------------------

* Fix issue of not being able to search from page 2+ in userlist, Fixes #40
* Fixed #44 </tr> tag now in correct place for valid html
* Fixed bug in get_available_time and created a test to make sure it's correct
* Allow PID to be specified in admin project form
* More testing


2.3.4 - 2010-05-26
------------------

* Decreased verbosity in management scripts
* Split user forms up one with username/password, one without
* Don't update datastore when saving a user in create script
* Only require required attributes in create_new_user method
* Moved to using django-simple-captcha instead of custom one
* Changed ordering when updating users in ldap datastore. Fixes #41
* More unit tests


2.3.3 - 2010-05-19
------------------

* Gecos and gidNumber are now also configurable via ldap_attrs


2.3.2 - 2010-05-19
------------------

* Pull in django-south dependency


2.3.1 - 2010-05-19
------------------

* Use active institutes in forms


2.3 - 2010-05-19
----------------

* Use Django-south for DB migrations
* Added is_active field to Institute


2.2.1 - 2010-05-17
-------------------

* Fixed create_account bug with ldap_attrs


2.2 - 2010-05-17
----------------

* Use dynamic values when creating an LDAP account. Also supply default_project when creating accounts
* Code clean up
* Added unittests for people and set up testing framework and project
* Bugfix for graphs when no machines
* Quota equals zero bug and signals to add IntituteChuck automatically
* Show jobID in default usage list.
* Added pylint file


2.1.1 - 2010-05-07
------------------

* Ability to set LOCKED_SHELL. Fixes #34
* objectClass now configurable


2.1 - 2010-05-06
----------------

* Changed size of cpu_job.jobname from 20 -> 100. REQUIRES DB change
* removed is_expertise from user project form
* By default expect a non expertise project when creating a project ID
* Removed VPAC in text on admin person form


2.0.16 - 2010-05-05
-------------------

* Better way of checking to see if user is locked or not


2.0.15 - 2010-05-05
-------------------

* Removed VPAC specific lock DN


2.0.14 - 2010-05-03
-------------------

* Fixed usage bug when no projectchunk
* Fixed JS broken link on project form


2.0.13 - 2010-05-03
-------------------

* Added initial data for default MachineCategory. Fixes #31
* Added initial api docs
* Added some management commands for clearing and populating
  usage cache and locking expired users
* Don't display title if it doesn't exist. Fixes #30


2.0.12 - 2010-04-29
-------------------

* Attempts to fix usage error. addresses #25


2.0.11 - 2010-04-28
-------------------

* Fixed broken graph urls


2.0.10 - 2010-04-28
-------------------

* Provide GRAPH_URL in template context


2.0.9 - 2010-04-28
------------------

* GRAPH_URL and GRAPH_ROOT settings if graph dir separate to MEDIA_*


2.0.8 - 2010-04-01
------------------

* Fixed software_detail bug


2.0.7 - 2010-03-31
------------------

* Fixed totals displaying in usage_institute_detail page
* Use new django aggregation support instead of raw sql
* Show project usage based on machine_category


2.0.6 - 2010-03-24
------------------

* Fixed bug in project reports url redirection


2.0.5 - 2010-03-22
------------------

* Depend on django-xmlrpc package


2.0.4 - 2010-03-22
------------------

* Actually use new alogger library


2.0.3 - 2010-03-22
------------------

* Depend on python-alogger


2.0.2 - 2010-03-19
------------------

* Fixed gdchart2 requirment


2.0.1 - 2010-03-19
------------------

* Initial release.
