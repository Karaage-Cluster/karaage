# Globally defined Karaage settings
# These settings will be used for karaage-admin and/or karaage-registration
###
### Standard Django settings 
### see http://docs.djangoproject.com/en/1.2/ref/settings/#ref-settings
###

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# If you must have karaage working on http only connection, uncomment the following:
# SESSION_COOKIE_SECURE = False

# Will receive error reports if something goes wrong
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'ATOMIC_REQUESTS': True,
    }
}

# Defaults used for error reports
SERVER_EMAIL = 'karaage@example.org'
EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[Karaage] - '

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Australia/Melbourne'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-au'

# Unique key used for storing session data etc.
SECRET_KEY = ''

###
### Karaage settings
###

# Used in various places
ACCOUNTS_EMAIL = 'accounts@example.com'
ACCOUNTS_ORG_NAME = 'Example'
# Address email is sent to for admin approval
APPROVE_ACCOUNTS_EMAIL = ACCOUNTS_EMAIL

LOCKED_SHELL = '/usr/local/sbin/insecure'

# Registration base URL - Used in email templates
# Uncomment to override default
# REGISTRATION_BASE_URL = 'https://<hostname>/users'

# SHIB_SUPPORTED = False
