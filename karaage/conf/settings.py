from karaage.conf.defaults import *

PLUGINS = []

exec(open("/etc/karaage3/settings.py", "rb").read())

DEFAULT_FROM_EMAIL = ACCOUNTS_EMAIL


def load_plugins(plugins):
    global INSTALLED_APPS
    global XMLRPC_METHODS

    import importlib
    for plugin in plugins:
        module_name, descriptor_name = plugin.rsplit(".", 1)
        module = importlib.import_module(module_name)
        descriptor = getattr(module, descriptor_name)
        assert descriptor.plugin == "karaage3"

        INSTALLED_APPS = (descriptor.module,) + descriptor.requires \
            + INSTALLED_APPS

        XMLRPC_METHODS = descriptor.xmlrpc_methods + XMLRPC_METHODS

load_plugins(PLUGINS)
