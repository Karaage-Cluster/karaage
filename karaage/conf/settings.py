# Package defined Karaage Settings

AUTH_PROFILE_MODULE = 'people.Person'

GRAPH_DEBUG = False
GRAPH_LIB = 'karaage.graphs.matplotlib9'
GRAPH_ROOT = '/var/cache/karaage/graphs'
GRAPH_URL = '/kgadmin_graphs/'

DEFAULT_MC = 1

SHELLS = ( ('/bin/bash','bash'),
           ('/bin/csh', 'csh'),
           ('/bin/ksh', 'ksh'),
           ('/bin/tcsh', 'tcsh'),
           ('/bin/zsh', 'zsh'), )
   

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.flatpages',
    'south',
    'andsome.layout',
    'andsome',
    'django_surveys',
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
    'placard',
    'placard.lgroups',
    'placard.lusers',
    'django_xmlrpc',
    'django_pbs.servers',
    'django_pbs.jobs',
    'django.contrib.comments',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/etc/karaage/templates",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'karaage.context_processors.common',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/django_media/'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

AUTHENTICATION_BACKENDS = (
    'placard.backends.LDAPBackend',
)

LDAP_ATTRS = 'karaage.conf.ldap_attrs'
LDAP_PASSWD_SCHEME = 'md5-crypt'

from os import uname
SERVER_EMAIL = 'karaage@' + uname()[1]
EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[Karaage] - '

SEND_BROKEN_LINK_EMAILS = True

USER_OBJECTCLASS = ['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount',]
ACCOUNT_OBJECTCLASS = ['top','person','organizationalPerson','inetOrgPerson', 'shadowAccount','posixAccount']


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

execfile("/etc/karaage/global_settings.py")
