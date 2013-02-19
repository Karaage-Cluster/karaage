# Django settings for grunt project.
from os import uname

GRAPH_DEBUG = True

GRAPH_LIB = 'karaage.graphs.matplotlib9'

ADMIN_APPROVE_ACCOUNTS = True

PROJECT_DATASTORE = 'karaage.datastores.projects.ldap_datastore'
INSTITUTE_DATASTORE = 'karaage.datastores.institutes.ldap_datastore'
PERSONAL_DATASTORE = 'karaage.datastores.openldap_datastore'

ACCOUNTS_ORG_NAME = 'TestOrg'

ACCOUNT_DATASTORES = {
    1: 'karaage.datastores.openldap_datastore',
    2: 'karaage.datastores.dummy',
}

LOCKED_SHELL = '/usr/local/sbin/insecure'
BOUNCED_SHELL = '/usr/local/sbin/bouncedemail'

USER_OBJECTCLASS = ['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount',]
ACCOUNT_OBJECTCLASS = ['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount','posixAccount']


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
        'ENGINE': 'tldap.backend.transaction',
        'URI': 'ldap://localhost:38911/',
        'USER': 'cn=Manager,dc=python-ldap,dc=org',
        'PASSWORD': 'password',
        'USE_TLS': False,
        'TLS_CA' : None,
        'LDAP_ACCOUNT_BASE': 'ou=People, dc=python-ldap,dc=org',
        'LDAP_GROUP_BASE': 'ou=Group, dc=python-ldap,dc=org'
    }
}

PLACARD_MASTER = {
    'NAME': 'OpenLDAP',
    'LDAP': 'default',
    'ACCOUNT': 'placard.test.schemas.rfc_account',
    'GROUP': 'placard.test.schemas.rfc_group',
}

HOME_DIRECTORY = "/vpac/%(default_project)s/%(uid)s"

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
GRAPH_URL = MEDIA_URL + 'graphs/'

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'karaage.context_processors.common',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'andsome.middleware.threadlocals.ThreadLocals',  
)


ROOT_URLCONF = 'testproject.urls'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.flatpages',
    'andsome.layout',
    'andsome',
    'captcha',
    'karaage',
    'karaage.people',
    'karaage.machines',
    'karaage.institutes',
    'karaage.projects',
    'karaage.usage',
    'karaage.requests',
    'karaage.cache',
    'karaage.software',
    'karaage.pbsmoab',
    'karaage.projectreports',
    'karaage.emails',
    'karaage.applications',
    'placard',
    'django_pbs.servers',
    'django_pbs.jobs',
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
