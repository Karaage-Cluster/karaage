from karaage.conf.defaults import *

exec(open("/etc/karaage3/global_settings.py", "rb").read())

DEFAULT_FROM_EMAIL = ACCOUNTS_EMAIL
