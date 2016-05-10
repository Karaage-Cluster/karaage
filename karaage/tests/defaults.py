# Copyright 2014-2015 VPAC
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
import os
import os.path
import environ

env = environ.Env()


class InvalidString(str):

    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        raise TemplateSyntaxError(
            "Undefined variable or unknown value for: \"%s\"" % other)

TEMPLATE_STRING_IF_INVALID = InvalidString("%s")

DEBUG = True
DEBUG_SERVE_STATIC = True
PIPELINE_ENABLED = True
TEMPLATE_DEBUG = DEBUG
SHIB_SUPPORTED = True
SOUTH_TESTS_MIGRATE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s '
            '%(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'py.warnings': {
            # kg-manage test will automatically add a handler here
            # if verbosity is >= 0.
            'handlers': ["null"],
            'propagate': False,
        },
    },
}
# DATASTORES

MACHINE_CATEGORY_DATASTORES = {
    'ldap': [
    ],
    'dummy': [
    ],
}

# OTHER

ACCOUNTS_ORG_NAME = 'TestOrg'

DATABASES = {'default': env.db(default="sqlite:///")}

LDAP = {
    'default': {
        'ENGINE': 'tldap.backend.fake_transactions',
        'URI': 'ldap://localhost:38911/',
        'USER': 'cn=Manager,dc=python-ldap,dc=org',
        'PASSWORD': 'password',
        'USE_TLS': False,  # Legacy, for TLDAP <= 0.2.16
        'REQUIRE_TLS': False,
        'START_TLS ': False,
        'TLS_CA': None,
    }
}

LDAP_TEST_DATASTORE = 'ldap'
LDAP_TEST_DATASTORE_N = 0

SERVER_EMAIL = 'django@' + os.uname()[1]
ACCOUNTS_EMAIL = 'accounts@vpac.org'
EMAIL_SUBJECT_PREFIX = '[Grunt VPAC] - '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TIME_ZONE = 'Australia/Melbourne'
LANGUAGE_CODE = 'en-au'

TMP_DIR = 'tmp'

INTERNAL_IPS = (
    '127.0.0.1',
)

AUP_URL = 'http://example.com/aup.html'

REGISTRATION_BASE_URL = 'https://example.com/users'

SECRET_KEY = '5hvhpe6gv2t5x4$3dtq(w2v#vg@)sx4p3r_@wv%l41g!stslc*'

STATIC_ROOT = 'tmp/static'
STATIC_URL = "/static/"

TEST_MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))
FIXTURE_DIRS = (os.path.join(TEST_MODULE_ROOT),)

ENABLE_CRACKLIB = False
