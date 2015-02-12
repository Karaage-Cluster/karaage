# -*- coding: utf-8 -*-
# Copyright 2014-2015 VPAC
#
# Copyright 2014 The University of Melbourne
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

import importlib
import django
import warnings
from karaage.plugins import BasePlugin


def add_plugin(namespace, plugin_name, django_apps, depends):

    module_name, descriptor_name = plugin_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    descriptor = getattr(module, descriptor_name)
    assert issubclass(descriptor, BasePlugin)

    value = descriptor.depends
    depends.extend(value)

    if django.VERSION < (1, 7):
        value = descriptor.name
        assert value is not None
        django_apps.append(value)
    else:
        django_apps.append(plugin_name)

    value = descriptor.django_apps
    django_apps.extend(value)

    value = descriptor.xmlrpc_methods
    namespace.XMLRPC_METHODS += value

    value = descriptor.template_context_processors
    namespace.TEMPLATE_CONTEXT_PROCESSORS += value

    for key, value in descriptor.settings.items():
        try:
            getattr(namespace, key)
        except AttributeError:
            setattr(namespace, key, value)


def load_plugins(namespace, plugins):
    done = set()
    django_apps = []

    depends = plugins
    while len(depends) > 0:
        new_depends = []
        for plugin in depends:
            if plugin.startswith("kgapplications.") \
                    or plugin.startswith("kgsoftware.") \
                    or plugin.startswith("kgusage."):
                new_plugin = "karaage.plugins.%s" % plugin

                warnings.warn(
                    "%s is legacy, use %s instead"
                    % (plugin, new_plugin), DeprecationWarning)
                plugin = new_plugin

            if plugin not in done:
                add_plugin(namespace, plugin, django_apps, new_depends)
                done.add(plugin)
        depends = new_depends

    installed_apps = []
    done = set()

    for apps in [
        namespace.KARAAGE_APPS,
        django_apps,
        namespace.INSTALLED_APPS,
    ]:
        for app in apps:
            if app not in done:
                installed_apps.append(app)
                done.add(app)

    namespace.INSTALLED_APPS = installed_apps

    del namespace.KARAAGE_APPS


def post_process(namespace):
    http_host = namespace.HTTP_HOST
    for i, host in enumerate(namespace.ALLOWED_HOSTS):
        namespace.ALLOWED_HOSTS[i] = host % {'HOST': http_host}
    namespace.REGISTRATION_BASE_URL = \
        namespace.REGISTRATION_BASE_URL % {'HOST': http_host}
    namespace.ADMIN_BASE_URL = \
        namespace.ADMIN_BASE_URL % {'HOST': http_host}
    load_plugins(namespace, namespace.PLUGINS)
