# Django settings for grunt project.
from karaage.conf.defaults import *
from os import uname

AJAX_LOOKUP_CHANNELS = {
    'person' : ( 'karaage.people.lookups', 'PersonLookup'),
    'group' : ( 'karaage.people.lookups', 'GroupLookup'),
    'project' : ( 'karaage.projects.lookups', 'ProjectLookup'),
}

class InvalidString(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        raise TemplateSyntaxError(
            "Undefined variable or unknown value for: \"%s\"" % other)

TEMPLATE_STRING_IF_INVALID = InvalidString("%s")

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SHIB_SUPPORTED = False
GRAPH_DEBUG = True
SOUTH_TESTS_MIGRATE = False

# DATASTORES

DATASTORES = {
    'ldap' : [
        {
            'DESCRIPTION': 'Default LDAP datastore',
            'ENGINE': 'karaage.datastores.ldap.AccountDataStore',
            'LDAP': 'default',
            'ACCOUNT': 'karaage.datastores.ldap_schemas.openldap_account',
            'GROUP': 'karaage.datastores.ldap_schemas.openldap_group',
            'PRIMARY_GROUP': "institute",
            'DEFAULT_PRIMARY_GROUP': "dummy",
            'HOME_DIRECTORY': "/vpac/%(default_project)s/%(uid)s",
            'LOCKED_SHELL': '/usr/local/sbin/insecure',
        },
    ],
    'dummy' : [
    ],
}

# OTHER

ACCOUNTS_ORG_NAME = 'TestOrg'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'karaage.db',            # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

LDAP = {
    'default': {
        'ENGINE': 'tldap.backend.fake_transactions',
        'URI': 'ldap://localhost:38911/',
        'USER': 'cn=Manager,dc=python-ldap,dc=org',
        'PASSWORD': 'password',
        'USE_TLS': False,
        'TLS_CA' : None,
        'LDAP_ACCOUNT_BASE': 'ou=People, dc=python-ldap,dc=org',
        'LDAP_GROUP_BASE': 'ou=Group, dc=python-ldap,dc=org'
    }
}

LDAP_TEST_DATASTORE = 'ldap'
LDAP_TEST_DATASTORE_N = 0

SERVER_EMAIL = 'django@' + uname()[1]
ACCOUNTS_EMAIL = 'accounts@vpac.org'
APPROVE_ACCOUNTS_EMAIL = ACCOUNTS_EMAIL
EMAIL_SUBJECT_PREFIX = '[Grunt VPAC] - '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TIME_ZONE = 'Australia/Melbourne'
LANGUAGE_CODE = 'en-au'

ROOT_URLCONF = 'urls'

GRAPH_ROOT = '/tmp/graphs/'
GRAPH_TMP = '/tmp/matplotlib/'
GRAPH_URL = '/media/graphs/'

INTERNAL_IPS = (
    '127.0.0.1',
    )

AUP_URL = 'http://example.com/aup.html'

ALLOW_REGISTRATIONS = True
REGISTRATION_BASE_URL = 'https://example.com/users'

SECRET_KEY = '5hvhpe6gv2t5x4$3dtq(w2v#vg@)sx4p3r_@wv%l41g!stslc*'

STATIC_URL = "/static/"
