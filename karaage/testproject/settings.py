# Django settings for grunt project.
from os import uname

AUTH_USER_MODEL = 'people.Person'

AJAX_LOOKUP_CHANNELS = {
    'person' : ( 'karaage.people.lookups', 'PersonLookup'),
    'group' : ( 'karaage.people.lookups', 'GroupLookup'),
    'project' : ( 'karaage.projects.lookups', 'ProjectLookup'),
}

AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = "staticfiles"

GRAPH_DEBUG = True

SHIB_SUPPORTED = False
SHIB_ATTRIBUTE_MAP = {
    "HTTP_SHIB_IDENTITY_PROVIDER": (True, "idp"),
    "HTTP_PERSISTENT_ID": (True, "persistent_id"),
    "HTTP_MAIL": (True, "email"),
    "HTTP_GIVENNAME": (True, "first_name"),
    "HTTP_SN": (True, "last_name"),
    "HTTP_TELEPHONENUMBER": (False, "telephone"),
    }



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

BOUNCED_SHELL = '/usr/local/sbin/bouncedemail'

DEFAULT_MC = 1
AUTH_PROFILE_MODULE = 'people.Person'

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

LDAP_SCHEMA_FILE = "conf/ldap_schemas.py"

SERVER_EMAIL = 'django@' + uname()[1]
ACCOUNTS_EMAIL = 'accounts@vpac.org'
APPROVE_ACCOUNTS_EMAIL = ACCOUNTS_EMAIL
EMAIL_SUBJECT_PREFIX = '[Grunt VPAC] - '

SHELLS = ( ('/bin/bash','bash'),
           ('/bin/csh', 'csh'),
           ('/bin/ksh', 'ksh'),
           ('/bin/tcsh', 'tcsh'),
           ('/bin/zsh', 'zsh'), )
           

ADMINS = (
     ('Sam Morrison', 'sam@vpac.org'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Australia/Melbourne'
LANGUAGE_CODE = 'en-au'

MEDIA_ROOT = '/tmp'
MEDIA_URL = '/media/'
GRAPH_ROOT = MEDIA_ROOT + '/graphs/'
GRAPH_TMP = MEDIA_ROOT + '/matplotlib/'
GRAPH_URL = MEDIA_URL + 'graphs/'

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'karaage.common.context_processors.common',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'karaage.middleware.threadlocals.ThreadLocals',
)


ROOT_URLCONF = 'karaage.testproject.urls'


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'captcha',
    'karaage.common',
    'karaage.admin',
    'karaage.people',
    'karaage.machines',
    'karaage.institutes',
    'karaage.projects',
    'karaage.usage',
    'karaage.cache',
    'karaage.software',
    'karaage.pbsmoab',
    'karaage.projectreports',
    'karaage.emails',
    'karaage.applications',
    'tldap.methods',
    'karaage.test_data',
    'django_surveys',
)


LOCAL_PBS_SERVERS = []


INTERNAL_IPS = (
    '127.0.0.1',
    '172.25.10.10',
    )


AUP_URL = 'http://example.com/aup.html'

ALLOW_REGISTRATIONS = True
REGISTRATION_BASE_URL = 'https://example.com/users'

DEFAULT_SHELL = '/bin/bash'

SECRET_KEY = '5hvhpe6gv2t5x4$3dtq(w2v#vg@)sx4p3r_@wv%l41g!stslc*'

STATIC_URL = "/static/"
