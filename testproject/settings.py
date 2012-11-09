# Django settings for grunt project.
from os import uname, path as os_path

TEST_RUNNER='andsome.test_utils.xmlrunner.run_tests'

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

LDAP_URL = 'ldap://localhost:38911'
LDAP_USE_TLS=False
LDAP_ADMIN_PASSWORD="password"
LDAP_BASE="dc=python-ldap,dc=org"
LDAP_ADMIN_USER="cn=Manager,dc=python-ldap,dc=org"
LDAP_USER_BASE='ou=People, %s' % LDAP_BASE
LDAP_GROUP_BASE='ou=Groups, %s' % LDAP_BASE
LDAP_ATTRS = 'testproject.ldap_attrs'

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

DATABASE_ENGINE = 'sqlite3'

MEDIA_ROOT = '/tmp'
MEDIA_URL = '/media/'
GRAPH_ROOT = MEDIA_ROOT + '/graphs/'
GRAPH_URL = MEDIA_URL + 'graphs/'

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
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
    'placard.lgroups',
    'placard.lusers',
    'django_pbs.servers',
    'django_pbs.jobs',
    'karaage.test_data',

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
