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
import os
import os.path

import environ


env = environ.Env()


class InvalidString(str):

    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        raise TemplateSyntaxError(
            "Undefined variable or unknown value for: \"%s\"" % other)

# FIXME: TEMPLATES not accessible
# TEMPLATES[0]['OPTIONS']['string_if_invalid'] = InvalidString("%s")


DEBUG = True
SESSION_COOKIE_SECURE = False
PIPELINE_ENABLED = True
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

DATASTORES = []

# OTHER

ACCOUNTS_ORG_NAME = 'TestOrg'

DATABASES = {'default': env.db(default="sqlite:///")}

LDAP = {
    'default': {
        'ENGINE': 'tldap.backend.fake_transactions',
        'URI': os.environ['LDAP_URL'],
        'USER': os.environ['LDAP_DN'],
        'PASSWORD': os.environ['LDAP_PASSWORD'],
        'USE_TLS': False,  # Legacy, for TLDAP <= 0.2.16
        'REQUIRE_TLS': False,
        'START_TLS ': False,
        'TLS_CA': None,
    }
}

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

MIN_PASSWORD_LENGTH = 6
