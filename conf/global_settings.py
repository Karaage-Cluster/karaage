# Globally defined Karaage settings
# These settings will be used for karaage-admin and/or karaage-registration
###
### Standard Django settings 
### see http://docs.djangoproject.com/en/1.2/ref/settings/#ref-settings
###

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Multi DB Syntax (Django >= 1.2)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Single DB (Django < 1.2)
DATABASE_ENGINE = '' # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = '' # Or path to database file if using sqlite3.
DATABASE_USER = '' # Not used with sqlite3
DATABASE_PASSWORD = '' # Not used with sqlite3.
DATABASE_HOST = '' # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '' # Set to empty string for default. Not used with sqlite3.


# Defaults used for error reports
SERVER_EMAIL = 'karaage@example.org'
EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[Karaage] - '

# Default URLs for logging in
LOGIN_URL="/accounts/login/"
LOGIN_REDIRECT_URL="/"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Australia/Melbourne'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-au'

SITE_ID = 1

# Unique key used for storing session data etc.
# To generate this key run kg_set_secret_key
SECRET_KEY = ''

###
### Karaage settings
###

# Do new cluster accounts need a 2nd stage of approval
ADMIN_APPROVE_ACCOUNTS = True

PERSONAL_DATASTORE = 'karaage.datastores.openldap_datastore'

# Dictionary of MachineCategory.id and python module to use for storing accounts
ACCOUNT_DATASTORES = {
    1: 'karaage.datastores.openldap_datastore',
}

# Used in various places
ACCOUNTS_EMAIL = 'accounts@example.com'
ACCOUNTS_ORG_NAME = 'Example'

LOCKED_SHELL = '/usr/local/sbin/insecure'

###
### Placard Settings
### see - https://code.arcs.org.au/hudson/job/Placard/javadoc/
###


LDAP_URL = 'ldap://ldap.example.org'
LDAP_BASE = 'dc=example, dc=org'
LDAP_USER_BASE='ou=People, %s' % LDAP_BASE
LDAP_GROUP_BASE='ou=Groups, %s' % LDAP_BASE
LDAP_USE_TLS = False
LDAP_ADMIN_USER = 'cn=admin,dc=example,dc=org'
LDAP_ADMIN_PASSWORD = 'secret'

###
### Django PBS settings
###


LOCAL_PBS_SERVERS = [
    'cluster1.example.com',
    'cluster2.example.com',
]


