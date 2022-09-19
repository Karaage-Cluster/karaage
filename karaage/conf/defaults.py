# -*- coding: utf-8 -*-
# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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
from socket import getfqdn

import django
import environ
import six


HTTP_HOST = getfqdn()
env = environ.Env()

###
# DJANGO SETTINGS
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

# Do not change: The model to use to represent a Django user.
#
# If false, administrators can log in but don't get any special access. Used
# for karaage-registration.
AUTH_USER_MODEL = "karaage.Person"

# Default Auto field type
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Do not change: A tuple of strings designating all applications that are
# enabled in this Django installation. Each string should be a dotted Python
# path to:
#
# * an application configuration class, or a package containing a
# * application.
if django.VERSION < (1, 7):
    KARAAGE_APPS = ("karaage",)
else:
    KARAAGE_APPS = ("karaage.apps.Karaage",)

INSTALLED_APPS = (
    "captcha",
    "ajax_select",
    "django_tables2",
    "tldap.django",
    "pipeline",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.auth",
)

# A list containing the settings for all template engines to be used with
# Django. Each item of the list is a dictionary containing the options for an
# individual engine.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "/etc/karaage3/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "karaage.common.context_processors.common",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
            # 'string_if_invalid': InvalidString("%s"),
        },
    },
]
FORM_RENDERER = "django.forms.renderers.DjangoDivFormRenderer"
USE_TZ = True

# A boolean that specifies whether Django’s translation system should be
# enabled. This provides an easy way to turn it off, for performance. If this
# is set to False, Django will make some optimizations so as not to load the
# translation machinery.
USE_I18N = False

# A tuple of middleware classes to use.
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "karaage.middleware.threadlocals.ThreadLocals",
    "tldap.django.middleware.TransactionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# A tuple of authentication backend classes (as strings) to use when attempting
# to authenticate a user.

# The ``karaage.backends.LDAPBackend`` backend is legacy, to support upgrades
# from Karaage versions before 3.
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "karaage.backends.LDAPBackend",
)

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    # Commented out as not supported by Django 1.8:
    # 'django.contrib.auth.hashers.Argon2PasswordHasher',
    "django.contrib.auth.hashers.SHA1PasswordHasher",
]

# The default value for the X-Frame-Options header used by
# XFrameOptionsMiddleware. See the `clickjacking protection
# <https://docs.djangoproject.com/en/dev/ref/clickjacking/>`_ documentation.
X_FRAME_OPTIONS = "DENY"

# Whether to use a secure cookie for the session cookie. If this is set to
# True, the cookie will be marked as “secure,” which means browsers may ensure
# that the cookie is only sent under an HTTPS connection.
SESSION_COOKIE_SECURE = True

# Whether to expire the session when the user closes their browser. See
# `Browser-length sessions vs. persistent sessions
# <https://docs.djangoproject.com/en/dev/topics/http/sessions/
# browser-length-vs-persistent-sessions>`_.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# A string representing the full Python import path to your root URLconf. For
# example: "mydjangoapps.urls". Can be overridden on a per-request basis by
# setting the attribute urlconf on the incoming HttpRequest object.
ROOT_URLCONF = "karaage.conf.urls"

# The URL where requests are redirected for login, especially when
# using the login_required() decorator. Mostly not used anymore.
LOGIN_URL = "kg_profile_login"

# The absolute path to the directory where collectstatic will collect static
# files for deployment.
STATIC_ROOT = "/var/lib/karaage3/static"


# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = "/kgstatic/"

# A list of strings representing the host/domain names that this Django site
# can serve. This is a security measure to prevent an attacker from poisoning
# caches and password reset emails with links to malicious hosts by submitting
# requests with a fake HTTP Host header, which is possible even under many
# seemingly-safe web server configurations.
ALLOWED_HOSTS = ["%(HOST)s"]

###
# DJANGO PIPELINE
###

STATICFILES_STORAGE = "pipeline.storage.PipelineManifestStorage"

PIPELINE = {
    "EMBED_PATH": r"img/|images/",
    "CSS_COMPRESSOR": "pipeline.compressors.cssmin.CSSMinCompressor",
    "STYLESHEETS": {
        "karaage": {
            "source_filenames": (
                "css/*.css",
                "ajax_select/css/ajax_select.css",
            ),
            "output_filename": "min.css",
            "variant": "datauri",
        },
    },
    "JS_COMPRESSOR": "pipeline.compressors.jsmin.JSMinCompressor",
    "JAVASCRIPT": {
        "karaage": {
            "source_filenames": (
                "js/jquery-1.11.2.js",
                "js/jquery-ui-1.11.4.js",
                "js/*.js",
                "ajax_select/js/ajax_select.js",
            ),
            "output_filename": "min.js",
        }
    },
}


###
# AJAX SETTINGS
###

# Channels for django-ajax-selects.
AJAX_LOOKUP_CHANNELS = {
    "person": ("karaage.people.lookups", "PersonLookup"),
    "group": ("karaage.people.lookups", "GroupLookup"),
    "institute": ("karaage.institutes.lookups", "InstituteLookup"),
    "project": ("karaage.projects.lookups", "ProjectLookup"),
}

# Automatically load media files required for django-ajax-selects.
AJAX_SELECT_BOOTSTRAP = True


###
# KARAAGE SETTINGS
###

# SETTINGS FROM DOCKER
VERSION = env("VERSION", default=None)
BUILD_DATE = env("BUILD_DATE", default=None)
VCS_REF = env("VCS_REF", default=None)
SLURM_VER = env("SLURM_VER", default=None)

# DIRECTORY FOR TEMP FILES
TMP_DIR = "/var/cache/karaage3/tmp/"

# DIRECTORY FOR SHARED FILES
FILES_DIR = "/var/lib/karaage3/files/"

# URL FOR SHARED FILES
FILES_URL = "/kgfiles/"

# List of shells that we support.
SHELLS = (
    ("/bin/bash", "bash"),
    ("/bin/csh", "csh"),
    ("/bin/ksh", "ksh"),
    ("/bin/tcsh", "tcsh"),
    ("/bin/zsh", "zsh"),
)

# Default shell we should use for new accounts.
DEFAULT_SHELL = "/bin/bash"

# List of global datastores and configurations for Karaage.
DATASTORES = []

# Do we support shibboleth for logins?
AAF_RAPID_CONNECT_ENABLED = False

# How do we interpret HTTP parameters as shibboleth values?
SHIB_ATTRIBUTE_MAP = {
    "HTTP_SHIB_IDENTITY_PROVIDER": (True, "idp"),
    "HTTP_PERSISTENT_ID": (True, "persistent_id"),
    "HTTP_MAIL": (True, "email"),
    "HTTP_GIVENNAME": (False, "first_name"),
    "HTTP_SN": (False, "last_name"),
    "HTTP_TELEPHONENUMBER": (False, "telephone"),
    "HTTP_UID": (False, "uid"),
}

# RE for validing a username.
USERNAME_VALIDATION_RE = r"[-\w]+"

# Error to display if username validation failed.
USERNAME_VALIDATION_ERROR_MSG = six.u("Usernames can only contain letters, numbers and underscores")
USERNAME_MAX_LENGTH = 255

# RE for validing a project.
PROJECT_VALIDATION_RE = r"[-\w]+"

# Max length of a project identifier
PROJECT_ID_MAX_LENGTH = 255

# Error to display if project validation failed.
PROJECT_VALIDATION_ERROR_MSG = six.u("Project names can only contain letters, numbers and underscores")

# RE for validing a group id.
GROUP_VALIDATION_RE = r"[-\w]+"

# Error to display if group validation failed.
GROUP_VALIDATION_ERROR_MSG = six.u("Group names can only contain letters, numbers and underscores")

# Used for lock_training_accounts and unlock_training_accounts commands.
TRAINING_ACCOUNT_PREFIX = "^train[0-9]+$"

# Registration base URL - Used in email templates.
REGISTRATION_BASE_URL = "https://%(HOST)s/karaage"

# Admin base URL - Used in email templates.
ADMIN_BASE_URL = "https://%(HOST)s/karaage"

# If true, only administrators can log on to site. Used for karaage-admin.
ADMIN_REQUIRED = False

# If false, administrators can log in but don't get any special access. Used
# for karaage-registration.
ADMIN_IGNORED = False

# Available formatting that can be used for displaying datetime fields on
# templates.
SHORT_DATE_FORMAT = "Y-m-d"
SHORT_DATETIME_FORMAT = "Y-m-d H:i"

# List of Karaage plugins
PLUGINS = []

# The name of the class to use for starting the test suite.
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# A list of identifiers of messages generated by the system check framework
# (i.e. ["models.W001"]) that you wish to permanently acknowledge and ignore.
# Silenced warnings will no longer be output to the console; silenced errors
# will still be printed, but will not prevent management commands from running.
SILENCED_SYSTEM_CHECKS = [
    # BooleanField does not have a default value
    "1_6.W002",
]

APPLICATION_PROJECT = {
    "start": {
        "type": "transition",
        "class": "karaage.plugins.kgapplications.views.transitions.TransitionOpen",
        "on_success": {
            "type": "goto",
            "key": "O",
        },
    },
    "O": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.aed.StateApplicantEnteringDetails",
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
        "on_reopen": {
            "type": "goto",
            "key": "start",
        },
        "on_duplicate": {
            "type": "goto",
            "key": "DUP",
        },
        "on_submit": {
            "type": "transition",
            "class": "karaage.plugins.kgapplications.views.transitions.TransitionSubmit",
            "on_success": {
                "type": "transition",
                "class": "karaage.plugins.kgapplications.views.transitions.TransitionSplit",
                "on_existing_project": {
                    "type": "goto",
                    "key": "L",
                },
                "on_new_project": {
                    "type": "goto",
                    "key": "D",
                },
                "on_error": {
                    "type": "goto",
                    "key": "R",
                },
            },
            "on_error": {
                "type": "goto",
                "key": "R",
            },
        },
    },
    "L": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateWaitingForLeader",
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
        "on_duplicate": {
            "type": "goto",
            "key": "DUP",
        },
        "on_approve": {
            "type": "goto",
            "key": "K",
        },
    },
    "D": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateWaitingForDelegate",
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
        "on_duplicate": {
            "type": "goto",
            "key": "DUP",
        },
        "on_approve": {
            "type": "goto",
            "key": "K",
        },
    },
    "K": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateWaitingForAdmin",
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
        "on_duplicate": {
            "type": "goto",
            "key": "DUP",
        },
        "on_approve": {
            "type": "transition",
            "class": "karaage.plugins.kgapplications.views.transitions.TransitionApprove",
            "on_password_needed": {
                "type": "goto",
                "key": "P",
            },
            "on_password_ok": {
                "type": "goto",
                "key": "C",
            },
            "on_error": {
                "type": "goto",
                "key": "K",
            },
        },
    },
    "P": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StatePassword",
        "on_submit": {
            "type": "goto",
            "key": "C",
        },
    },
    "C": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateCompleted",
        "on_archive": {
            "type": "goto",
            "key": "A",
        },
    },
    "A": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateArchived",
    },
    "R": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateDeclined",
        "on_archive": {
            "type": "goto",
            "key": "A",
        },
        "on_reopen": {
            "type": "goto",
            "key": "start",
        },
    },
    "DUP": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateDuplicateApplicant",
        "on_reopen": {
            "type": "goto",
            "key": "start",
        },
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
    },
}


APPLICATION_SOFTWARE = {
    "start": {
        "type": "transition",
        "class": "karaage.plugins.kgapplications.views.transitions.TransitionOpen",
        "on_success": {
            "type": "goto",
            "key": "O",
        },
    },
    "O": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateIntroduction",
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
        "on_submit": {
            "type": "transition",
            "class": "karaage.plugins.kgapplications.views.transitions.TransitionSubmit",
            "on_success": {"type": "goto", "key": "K"},
            "on_error": {"type": "goto", "key": "R"},
        },
    },
    "K": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateWaitingForAdminSoftware",
        "on_cancel": {
            "type": "goto",
            "key": "R",
        },
        "on_duplicate": {
            "type": "goto",
            "key": "DUP",
        },
        "on_approve": {
            "type": "transition",
            "class": "karaage.plugins.kgapplications.views.transitions.TransitionApprove",
            "on_password_needed": {
                "type": "goto",
                "key": "R",
            },
            "on_password_ok": {
                "type": "goto",
                "key": "C",
            },
            "on_error": {
                "type": "goto",
                "key": "R",
            },
        },
    },
    "C": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateCompleted",
        "on_archive": {
            "type": "goto",
            "key": "A",
        },
    },
    "A": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateArchived",
        "on_reopen": {
            "type": "goto",
            "key": "start",
        },
    },
    "R": {
        "type": "state",
        "class": "karaage.plugins.kgapplications.views.states.StateDeclined",
        "on_archive": {
            "type": "goto",
            "key": "A",
        },
        "on_reopen": {
            "type": "goto",
            "key": "start",
        },
    },
}
