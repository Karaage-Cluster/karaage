# Package defined Karaage Settings
LDAP_SCHEMA_FILE = "/etc/karaage/ldap_schemas.py"

AUTH_USER_MODEL = 'people.Person'

AJAX_LOOKUP_CHANNELS = {
}

AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = "staticfiles"

GRAPH_DEBUG = False
GRAPH_ROOT = '/var/cache/karaage/graphs'
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
    'andsome.layout',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_xmlrpc',
    'south',
    'andsome',
    'captcha',
    'django_surveys',
    'karaage',
    'karaage.people',
    'karaage.machines',
    'karaage.institutes',
    'karaage.projects',
    'karaage.requests',
    'karaage.usage',
    'karaage.cache',
    'karaage.software',
    'karaage.pbsmoab',
    'karaage.projectreports',
    'karaage.emails',
    'karaage.applications',
    'ajax_select',
    'tldap.methods',
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
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.core.context_processors.i18n',
    'django.contrib.messages.context_processors.messages',
    'karaage.context_processors.common',
    'andsome.context_processors.base_url',
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
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'andsome.middleware.threadlocals.ThreadLocals',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'karaage.middleware.saml.SamlUserMiddleware',
    'tldap.middleware.TransactionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'karaage.backends.LDAPBackend',
)

# DATA STORES

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
            'HOME_DIRECTORY': "/home/%(uid)s",
            'LOCKED_SHELL': "/usr/local/sbin/locked",
        },
    ],
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
    ('karaage.pbsmoab.xmlrpc.parse_usage', 'parse_usage',),
    ('karaage.pbsmoab.xmlrpc.project_under_quota', 'project_under_quota',),
    ('karaage.pbsmoab.xmlrpc.showquota', 'showquota',),
    ('karaage.pbsmoab.xmlrpc.get_disk_quota', 'get_disk_quota',),
    ('karaage.projects.xmlrpc.get_project', 'get_project',),
    ('karaage.projects.xmlrpc.change_default_project', 'change_default_project',),
    ('karaage.projects.xmlrpc.get_project_members', 'get_project_members',),
    ('karaage.projects.xmlrpc.get_projects', 'get_projects',),
    ('karaage.projects.xmlrpc.get_users_projects', 'get_users_projects',),
)

X_FRAME_OPTIONS = 'DENY'

from socket import getfqdn
REGISTRATION_BASE_URL = 'https://%s/users' % getfqdn()

#Overriden but here for code checking
ACCOUNTS_EMAIL = 'accounts@example.com'

execfile("/etc/karaage/global_settings.py")

DEFAULT_FROM_EMAIL = ACCOUNTS_EMAIL
