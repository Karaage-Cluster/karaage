Customizing Karaage
===================
Karaage can be customized for local requirements. Traditionally this was done
using undocumented methods that were fragile and prone to breakage on upgrades.

This document attempts to document a standard set of methods which will not
break through upgrades, or if breakage is required the procedure to fix the
problem will be documented as part of the upgrade procedure.

Configuration settings
----------------------
There are many settings in ``/etc/karaage3/settings.py`` that can be customized.

.. setting:: DEBUG

DEBUG
~~~~~
Default: ``False``

Never deploy a site into production with DEBUG turned on.

Did you catch that? NEVER deploy a site into production with DEBUG turned on.

One of the main features of debug mode is the display of detailed error
pages. If your app raises an exception when DEBUG is True, Django will
display a detailed traceback, including a lot of metadata about your
environment, such as all the currently defined Django settings (from
settings.py).

See :setting:`django:DEBUG`.


.. setting:: ALLOWED_HOSTS

ALLOWED_HOSTS
~~~~~~~~~~~~~
Default: ``[]`` (Empty list)

A list of strings representing the host/domain names that this Django site can
serve. This is a security measure to prevent an attacker from poisoning caches
and password reset emails with links to malicious hosts by submitting requests
with a fake HTTP ``Host`` header, which is possible even under many
seemingly-safe web server configurations.

See :setting:`django:ALLOWED_HOSTS`.


.. setting:: SESSION_COOKIE_SECURE

SESSION_COOKIE_SECURE
~~~~~~~~~~~~~~~~~~~~~
Default: ``True``

Whether to use a secure cookie for the CSRF cookie. If this is set to ``True``,
the cookie will be marked as "secure," which means browsers may ensure that the
cookie is only sent under an HTTPS connection.

See :setting:`django:SESSION_COOKIE_SECURE`.


.. setting:: ADMINS

ADMINS
~~~~~~
Default: ``()`` (Empty tuple)

A tuple that lists people who get code error notifications. When
``DEBUG=False`` and a view raises an exception, Django will email these people
with the full exception information. Each member of the tuple should be a tuple
of (Full name, email address).

See :setting:`django:ADMINS`.


.. setting:: MANAGERS

MANAGERS
~~~~~~~~
Default: ``()`` (Empty tuple)

A tuple in the same format as :setting:`ADMINS` that specifies who should get
broken link notifications when
:py:class:`~django.middleware.common.BrokenLinkEmailsMiddleware` is enabled.

See :setting:`django:MANAGERS`.


.. setting:: DATABASES

DATABASES
~~~~~~~~~
Default: ``{}`` (Empty dictionary)

A tuple in the same format as :setting:`ADMINS` that specifies who should get
broken link notifications when
:py:class:`~django.middleware.common.BrokenLinkEmailsMiddleware` is enabled.

See :setting:`django:DATABASES`.


.. setting:: SERVER_EMAIL

SERVER_EMAIL
~~~~~~~~~~~~
Default: ``'root@localhost'``

The email address that error messages come from, such as those sent to
:setting:`ADMINS` and :setting:`MANAGERS`.

See :setting:`django:SERVER_EMAIL`.


.. setting:: EMAIL_HOST

EMAIL_HOST
~~~~~~~~~~
Default: ``'localhost'``

The host to use for sending email.

See :setting:`django:EMAIL_HOST`.


.. setting:: EMAIL_SUBJECT_PREFIX

EMAIL_SUBJECT_PREFIX
~~~~~~~~~~~~~~~~~~~~
Default: ``'[Django] '``

Subject-line prefix for email messages sent with ``django.core.mail.mail_admins``
or ``django.core.mail.mail_managers``. You'll probably want to include the
trailing space.

See :setting:`django:EMAIL_SUBJECT_PREFIX`.

.. setting:: TIME_ZONE

TIME_ZONE
~~~~~~~~~
Default: ``'America/Chicago'``

A string representing the time zone for this installation, or ``None``. See
the `list of time zones`_.

See :setting:`django:TIME_ZONE`.


.. setting:: LANGUAGE_CODE

LANGUAGE_CODE
~~~~~~~~~~~~~
Default: ``'en-us'``

A string representing the language code for this installation. This should be in
standard :term:`language ID format <language code>`. For example, U.S. English
is ``"en-us"``. See also the `list of language identifiers`_.

See :setting:`django:LANGUAGE_CODE`.


.. setting:: SECRET_KEY

SECRET_KEY
~~~~~~~~~~
Default: ``''`` (Empty string)

A secret key for a particular Django installation. This is used to provide
cryptographic signing, and should be set to a unique, unpredictable value.

See :setting:`django:SECRET_KEY`.

.. setting:: LOGGING

LOGGING
~~~~~~~
Default: A logging configuration dictionary.

A data structure containing configuration information. The contents of
this data structure will be passed as the argument to the
configuration method described in :setting:`LOGGING_CONFIG`.

See :setting:`django:LOGGING`.


.. setting:: ACCOUNTS_EMAIL

ACCOUNTS_EMAIL
~~~~~~~~~~~~~~
Default: No default; must be set

Users are advised to contact this address if having problems.
This is also used as the from address in outgoing emails.


.. setting:: ACCOUNTS_ORG_NAME


ACCOUNTS_ORG_NAME
~~~~~~~~~~~~~~~~~
Default: No default; must be set

This organisation name, used in outgoing emails.


.. setting:: REGISTRATION_BASE_URL

REGISTRATION_BASE_URL
~~~~~~~~~~~~~~~~~~~~~
Default: ``'https://<hostname>/users'``

Registration base URL - Used in email templates.


.. setting:: ADMIN_BASE_URL

ADMIN_BASE_URL
~~~~~~~~~~~~~~
Default: ``'https://<hostname>/kgadmin'``

Admin base URL - Used in email templates.


.. setting:: SHIB_SUPPORTED

SHIB_SUPPORTED
~~~~~~~~~~~~~~
Default: False

Is Shibboleth supported?


.. setting:: AUP_URL

AUP_URL
~~~~~~~
Default: Django template ``karaage/common/aup-detail.html``

Path to AUP policy. Note that setting this will not disable the Karaage
default page, it might be better to replace the AUP with a file in
the templates directory ``karaage/common/aup-detail.html`` if required.


.. setting:: ALLOW_REGISTRATIONS

ALLOW_REGISTRATIONS
~~~~~~~~~~~~~~~~~~~
Default: False

Do we allow anonymous users to request accounts?


.. setting:: USAGE_IS_PUBLIC

USAGE_IS_PUBLIC
~~~~~~~~~~~~~~~
Do we allow any logged in user to access all usage information?


.. setting:: EMAIL_MATCH_TYPE

EMAIL_MATCH_TYPE
~~~~~~~~~~~~~~~~
default: ``'exclude'``

Settings to restrict the valid list of email addresses we allow in
applications.  :setting:`EMAIL_MATCH_TYPE` can be ``'include'`` or
``'exclude'``.  If ``'include'`` then the email address must match one of the
RE entries in :setting:`EMAIL_MATCH_LIST`.  If ``'exclude'`` then then email
address must not match of the the RE entries in :setting:EMAIL_MATCH_LIST.


.. setting:: EMAIL_MATCH_LIST

EMAIL_MATCH_LIST
~~~~~~~~~~~~~~~~
Default: allow any email address

Settings to restrict the valid list of email addresses we allow in
applications.  :setting:`EMAIL_MATCH_TYPE` can be ``'include'`` or
``'exclude'``.  If ``'include'`` then the email address must match one of the
RE entries in :setting:`EMAIL_MATCH_LIST`.  If ``'exclude'`` then then email
address must not match of the the RE entries in :setting:EMAIL_MATCH_LIST.


.. setting:: PLUGINS

PLUGINS
~~~~~~~
Default: ``[]`` (Empty list)

A list of classes that define Karaage plugins. For more information on
creating plugins from scratch, please see the Karaage programmers
documentation.


.. setting:: PIPELINE_CSS_COMPRESSOR

PIPELINE_CSS_COMPRESSOR
~~~~~~~~~~~~~~~~~~~~~~~
Default: ``'pipeline.compressors.yui.YUICompressor'``

Compressor class to be applied to CSS files.

If empty or None, CSS files won’t be compressed.

See :setting:`django:PIPELINE_CSS_COMPRESSOR`.


.. setting:: PIPELINE_JS_COMPRESSOR

PIPELINE_JS_COMPRESSOR
~~~~~~~~~~~~~~~~~~~~~~
Default: ``'pipeline.compressors.yui.YUICompressor'``

Django pipeline setting.

Compressor class to be applied to JS files.

If empty or None, JavaScript files won’t be compressed.


.. _list of language identifiers: http://www.i18nguy.com/unicode/language-identifiers.html

.. _list of time zones: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
