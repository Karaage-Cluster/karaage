# -*- coding: utf-8 -*-

# Globally defined Karaage settings
# These settings will be used for karaage-admin and karaage-registration.

# Some of these values have sensible defaults. Settings that don't have a sensible
# default must be configured manually.

# Other Django settings are also possible, this list is not a comprehensive
# list of all settings.

###
### Django settings
###

# A boolean that turns on/off debug mode.
#
# Never deploy a site into production with DEBUG turned on.
#
# Did you catch that? NEVER deploy a site into production with DEBUG turned on.
#
# One of the main features of debug mode is the display of detailed error
# pages. If your app raises an exception when DEBUG is True, Django will
# display a detailed traceback, including a lot of metadata about your
# environment, such as all the currently defined Django settings (from
# settings.py).
#
# default: DEBUG = False
#
# DEBUG = False

# A list of strings representing the host/domain names that this Django site
# can serve. This is a security measure to prevent an attacker from poisoning
# caches and password reset emails with links to malicious hosts by submitting
# requests with a fake HTTP Host header, which is possible even under many
# seemingly-safe web server configurations.
ALLOWED_HOSTS = [ "www.example.org" ]

# Whether to use a secure cookie for the session cookie. If this is set to
# True, the cookie will be marked as “secure,” which means browsers may ensure
# that the cookie is only sent under an HTTPS connection.
#
# default: SESSION_COOKIE_SECURE = True
#
# SESSION_COOKIE_SECURE = False

# A tuple that lists people who get code error notifications. When DEBUG=False
# and a view raises an exception, Django will email these people with the full
# exception information. Each member of the tuple should be a tuple of (Full
# name, email address).
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# A tuple in the same format as ADMINS that specifies who should get broken
# link notifications when BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ADMINS

# A dictionary containing the settings for all databases to be used with
# Django. It is a nested dictionary whose contents maps database aliases to a
# dictionary containing the options for an individual database.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'ATOMIC_REQUESTS': True,
    }
}

# The email address that error messages come from, such as those sent to ADMINS
# and MANAGERS.
SERVER_EMAIL = 'karaage@example.org'

# The host to use for sending email.
EMAIL_HOST = 'localhost'

# Subject-line prefix for email messages sent with django.core.mail.mail_admins
# or django.core.mail.mail_managers. You’ll probably want to include the
# trailing space.
EMAIL_SUBJECT_PREFIX = '[Karaage] - '

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Australia/Melbourne'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-au'

# A secret key for a particular Django installation. This is used to provide
# cryptographic signing, and should be set to a unique, unpredictable value.
SECRET_KEY = ''

# A data structure containing configuration information. The contents of this
# data structure will be passed as the argument to the configuration method
# described in LOGGING_CONFIG.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/karaage/django.log',
            'formatter': 'verbose',
        },
        'karaage_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/karaage/karaage.log',
            'formatter': 'verbose',
        },
#        'ldap_file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': '/var/log/karaage/ldap.log',
#            'formatter': 'verbose',
#        },
#        'gold_file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': '/var/log/karaage/gold.log',
#            'formatter': 'verbose',
#       },
#       'slurm_file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': '/var/log/karaage/slurm.log',
#            'formatter': 'verbose',
#        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'karaage': {
            'handlers': ['karaage_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
#        'karaage.datastores.ldap': {
#            'handlers': ['ldap_file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#        'karaage.datastores.gold': {
#            'handlers': ['gold_file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#        'karaage.datastores.slurm': {
#            'handlers': ['slurm_file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
    },
}


###
### Karaage settings
###

# Users are advised to contact this address if having problems.
# This is also used as the from address in outgoing emails.
ACCOUNTS_EMAIL = 'accounts@example.com'

# This organisation name, used in outgoing emails.
ACCOUNTS_ORG_NAME = 'Example'

# Registration base URL - Used in email templates
# Uncomment to override default
#
# default: REGISTRATION_BASE_URL = 'https://<hostname>/users'
#
# REGISTRATION_BASE_URL = 'https://accounts.example.org/users'

# Is Shibboleth supported?
#
# default: SHIB_SUPPORTED = False
#
# SHIB_SUPPORTED = True

# Path to AUP policy. Note that setting this will not disable the Karaage
# default page, it might be better to replace the AUP with a file in
# /etc/karaage/templates/aup.html if required.
#
# default: Django template
#
# AUP_URL = "https://site.example.org/users/aup/"

# Do we allow anonymous users to request accounts?
#
# default:  ALLOW_REGISTRATIONS = False
#
# ALLOW_REGISTRATIONS = False

# Do we allow any logged in user to access all usage information?
#
# default: USAGE_IS_PUBLIC = True
#
# USAGE_IS_PUBLIC = False

# Settings to restrict the valid list of email addresses we allow in
# applications.  EMAIL_MATCH_TYPE can be "include" or "exclude".  If "include"
# then the email address must match one of the RE entries in EMAIL_MATCH_LIST.
# If "exclude" then then email address must not match of the the RE entries in
# EMAIL_MATCH_LIST.
# 
# default: allow any email address
#
# EMAIL_MATCH_TYPE="include"
# EMAIL_MATCH_LIST=["@vpac.org$", "@v3.org.au$", "^tux@.*au$"]
