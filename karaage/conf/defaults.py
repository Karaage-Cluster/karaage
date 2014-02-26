# -*- coding: utf-8 -*-
#
# Copyright 2007-2014 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

""" Default Karaage Settings. """

###
### DJANGO SETTINGS
###

# A boolean that turns on/off debug mode.
#
# Never deploy a site into production with DEBUG turned on.
#
# Did you catch that? NEVER deploy a site into production with DEBUG turned on.
#
# One of the main features of debug mode is the display of detailed error
# pages.  If your app raises an exception when DEBUG is True, Django will
# display a detailed traceback, including a lot of metadata about your
# environment, such as all the currently defined Django settings (from
# settings.py).
DEBUG = False

# A boolean that turns on/off template debug mode. If this is True, the fancy
# error page will display a detailed report for any exception raised during
# template rendering. This report contains the relevant snippet of the template,
# with the appropriate line highlighted.
#
# Note that Django only displays fancy error pages if DEBUG is True, so you’ll
# want to set that to take advantage of this setting.
TEMPLATE_DEBUG = True

# Do not change: The model to use to represent a Django user.
#
# If false, administrators can log in but don't get any special access. Used
# for karaage-registration.
AUTH_USER_MODEL = 'people.Person'

# Do not change: A tuple of strings designating all applications that are
# enabled in this Django installation. Each string should be a dotted Python
# path to:
#
# * an application configuration class, or a package containing a
# * application.
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
    'ajax_select',
    'jsonfield',
    'djcelery',
    'tldap.methods',
    'karaage.common',
    'karaage.legacy.admin',
    'karaage.people',
    'karaage.machines',
    'karaage.institutes',
    'karaage.projects',
    'karaage.usage',
    'karaage.legacy.cache',
    'karaage.software',
    'karaage.legacy.pbsmoab',
    'karaage.emails',
    'karaage.applications',
)

# List of locations of the template source files searched by
# django.template.loaders.filesystem.Loader, in search order.

# Allow administrator to override templates. 
TEMPLATE_DIRS = (
    "/etc/karaage/templates",
)

# A tuple of callables that are used to populate the context in
# RequestContext. These callables take a request object as their argument and
# return a dictionary of items to be merged into the context. 
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

# A tuple of template loader classes, specified as strings. Each Loader class
# knows how to import templates from a particular source. Optionally, a tuple
# can be used instead of a string. The first item in the tuple should be the
# Loader’s module, subsequent items are passed to the Loader during
# initialization. 
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# A boolean that specifies whether Django’s translation system should be
# enabled. This provides an easy way to turn it off, for performance. If this is
# set to False, Django will make some optimizations so as not to load the
# translation machinery. 
USE_I18N = False

# A tuple of middleware classes to use.
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'karaage.middleware.threadlocals.ThreadLocals',
    'karaage.middleware.saml.SamlUserMiddleware',
    'tldap.middleware.TransactionMiddleware',
)

# A tuple of authentication backend classes (as strings) to use when attempting
# to authenticate a user.

# The ``karaage.backends.LDAPBackend`` backend is legacy, to support upgrades
# from Karaage versions before 3. 
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'karaage.backends.LDAPBackend',
)

# The default value for the X-Frame-Options header used by
# XFrameOptionsMiddleware. See the `clickjacking protection
# <https://docs.djangoproject.com/en/dev/ref/clickjacking/>`_ documentation. 
X_FRAME_OPTIONS = 'DENY'

# Whether to use a secure cookie for the session cookie. If this is set to
# True, the cookie will be marked as “secure,” which means browsers may ensure
# that the cookie is only sent under an HTTPS connection. 
SESSION_COOKIE_SECURE = True

# Whether to expire the session when the user closes their browser. See
# `Browser-length sessions vs. persistent sessions
# <https://docs.djangoproject.com/en/dev/topics/http/sessions/#browser-length-vs-persistent-sessions>`_.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# A string representing the full Python import path to your root URLconf. For
# example: "mydjangoapps.urls". Can be overridden on a per-request basis by
# setting the attribute urlconf on the incoming HttpRequest object. 
ROOT_URLCONF = 'karaage.conf.urls'


###
### AJAX SETTINGS
###

# Channels for django-ajax-selects.
AJAX_LOOKUP_CHANNELS = {
    'person' : ( 'karaage.people.lookups', 'PersonLookup'),
    'group' : ( 'karaage.people.lookups', 'GroupLookup'),
    'project' : ( 'karaage.projects.lookups', 'ProjectLookup'),
}

# Automatically load media files required for django-ajax-selects.
AJAX_SELECT_BOOTSTRAP = True


##
## XMLRPC
##

# List of all XMLRPC methods that we support.
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

###
### KARAAGE SETTINGS
###

# If True, force overwritting existing graphs when generating graphs.
GRAPH_DEBUG = False

# Where should graphs be saved?
GRAPH_ROOT = '/var/cache/karaage/graphs'

# Temporary directory for matplotlib.
GRAPH_TMP = '/var/cache/karaage/matplotlib'

# URL where graphs can be found.
GRAPH_URL = '/karaage_graphs/'

# Default machine category, used by legacy XMLRPC when client doesn't specify
# a machine name. 
DEFAULT_MC = 1

# List of shells that we support.
SHELLS = (
    ('/bin/bash', 'bash'),
    ('/bin/csh', 'csh'),
    ('/bin/ksh', 'ksh'),
    ('/bin/tcsh', 'tcsh'),
    ('/bin/zsh', 'zsh'),
)

# Default shell we should use for new accounts.
DEFAULT_SHELL = '/bin/bash'

# Change the shell to this value if emails start bouncing (manual process).
BOUNCED_SHELL = '/usr/local/sbin/bouncedemail'

# List of global datastores and configurations for Karaage.
GLOBAL_DATASTORES = [
]


# List of MC datastores and configurations for Karaage.
MACHINE_CATEGORY_DATASTORES = {
    'dummy' : [
    ],
}

# Can any logged in user access the usage information?
USAGE_IS_PUBLIC = True

# Do we support shibboleth for logins?
SHIB_SUPPORTED = False

# How do we interpret HTTP parameters as shibboleth values?
SHIB_ATTRIBUTE_MAP = {
    "HTTP_SHIB_IDENTITY_PROVIDER": (True, "idp"),
    "HTTP_PERSISTENT_ID": (True, "persistent_id"),
    "HTTP_MAIL": (True, "email"),
    "HTTP_GIVENNAME": (True, "first_name"),
    "HTTP_SN": (True, "last_name"),
    "HTTP_TELEPHONENUMBER": (False, "telephone"),
    }

# RE for validing a username.
USERNAME_VALIDATION_RE = '[-\w]+'

# Error to display if username validation failed.
USERNAME_VALIDATION_ERROR_MSG = u'Usernames can only contain letters, numbers and underscores'

# RE for validing a project.
PROJECT_VALIDATION_RE = '[-\w]+'

# Error to display if project validation failed.
PROJECT_VALIDATION_ERROR_MSG = u'Project names can only contain letters, numbers and underscores'

# RE for validing a group id.
GROUP_VALIDATION_RE = '[-\w]+'

# Error to display if group validation failed.
GROUP_VALIDATION_ERROR_MSG = u'Group names can only contain letters, numbers and underscores'

# Used for lock_training_accounts and unlock_training_accounts commands.
TRAINING_ACCOUNT_PREFIX = 'train'

# Registration base URL - Used in email templates.
from socket import getfqdn
REGISTRATION_BASE_URL = 'https://%s/users' % getfqdn()

# Do we allow anonymous users to request accounts?
ALLOW_REGISTRATIONS = False

# If true, only administrators can log on to site. Used for karaage-admin.
ADMIN_REQUIRED = False

# If false, administrators can log in but don't get any special access. Used
# for karaage-registration.
ADMIN_IGNORED = False
