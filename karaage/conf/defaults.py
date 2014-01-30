# Package defined Karaage Settings
AUTH_USER_MODEL = 'people.Person'

AJAX_LOOKUP_CHANNELS = {
}

AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = "staticfiles"

GRAPH_DEBUG = False
GRAPH_ROOT = '/var/cache/karaage/graphs'
GRAPH_TMP = '/var/cache/karaage/matplotlib'
GRAPH_URL = '/karaage_graphs/'

DEFAULT_MC = 1

SHELLS = (
    ('/bin/bash', 'bash'),
    ('/bin/csh', 'csh'),
    ('/bin/ksh', 'ksh'),
    ('/bin/tcsh', 'tcsh'),
    ('/bin/zsh', 'zsh'),
)

DEFAULT_SHELL = '/bin/bash'
BOUNCED_SHELL = '/usr/local/sbin/bouncedemail'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_xmlrpc',
    'south',
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
    'karaage.emails',
    'karaage.applications',
    'ajax_select',
    'tldap.methods',
    'jsonfield',
    'djcelery',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/etc/karaage/templates",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.core.context_processors.i18n',
    'django.contrib.messages.context_processors.messages',
    'karaage.common.context_processors.common',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

SEND_BROKEN_LINK_EMAILS = True

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'karaage.middleware.threadlocals.ThreadLocals',
    'karaage.middleware.saml.SamlUserMiddleware',
    'tldap.middleware.TransactionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'karaage.backends.LDAPBackend',
)

# DATA STORES

DATASTORES = {
    'dummy' : [
    ],
}

# OTHER

USAGE_IS_PUBLIC = False

SHIB_SUPPORTED = False

SHIB_ATTRIBUTE_MAP = {
    "HTTP_SHIB_IDENTITY_PROVIDER": (True, "idp"),
    "HTTP_PERSISTENT_ID": (True, "persistent_id"),
    "HTTP_MAIL": (True, "email"),
    "HTTP_GIVENNAME": (True, "first_name"),
    "HTTP_SN": (True, "last_name"),
    "HTTP_TELEPHONENUMBER": (False, "telephone"),
    }


TRAINING_ACCOUNT_PREFIX = 'train'

XMLRPC_METHODS = (
    ('karaage.usage.xmlrpc.parse_usage', 'parse_usage',),
    ('karaage.machines.xmlrpc.get_disk_quota', 'get_disk_quota',),
    ('karaage.projects.xmlrpc.get_project', 'get_project',),
    ('karaage.projects.xmlrpc.change_default_project', 'change_default_project',),
    ('karaage.projects.xmlrpc.get_project_members', 'get_project_members',),
    ('karaage.projects.xmlrpc.get_projects', 'get_projects',),
    ('karaage.projects.xmlrpc.get_users_projects', 'get_users_projects',),
    ('karaage.projects.xmlrpc.project_under_quota', 'project_under_quota',),
    ('karaage.projects.xmlrpc.showquota', 'showquota',),
)

X_FRAME_OPTIONS = 'DENY'

from socket import getfqdn
REGISTRATION_BASE_URL = 'https://%s/users' % getfqdn()
