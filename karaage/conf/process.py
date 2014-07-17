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


def add_plugin(namespace, plugin_name, django_apps, depends):

    import importlib
    module_name, descriptor_name = plugin_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    descriptor = getattr(module, descriptor_name)
    assert descriptor.plugin == "karaage3"

    try:
        value = descriptor.depends
    except:
        pass
    else:
        depends.extend(value)

    try:
        value = descriptor.module
    except:
        pass
    else:
        django_apps.append(value)

    try:
        value = descriptor.django_apps
    except:
        pass
    else:
        django_apps.extend(value)

    try:
        value = descriptor.xmlrpc_methods
    except:
        pass
    else:
        namespace.XMLRPC_METHODS += value

    for key, value in descriptor.settings.items():
        try:
            getattr(namespace, key)
            raise RuntimeError(
                'setting %s already exists error adding %s'
                % (key, plugin_name))
        except AttributeError:
            pass

        setattr(namespace, key, value)


def load_plugins(namespace, plugins):
    done = set()
    django_apps = []

    depends = plugins
    while len(depends) > 0:
        new_depends = []
        for plugin in depends:
            if plugin not in done:
                add_plugin(namespace, plugin, django_apps, new_depends)
                done.add(plugin)
        depends = new_depends

    installed_apps = []
    done = set()

    for app in namespace.KARAAGE_APPS:
        if app not in done:
            installed_apps.append(app)
            done.add(app)

    for app in django_apps:
        if app not in done:
            installed_apps.append(app)
            done.add(app)

    for app in namespace.INSTALLED_APPS:
        if app not in done:
            installed_apps.append(app)
            done.add(app)

    namespace.INSTALLED_APPS = installed_apps

    del namespace.KARAAGE_APPS


def post_process(namespace):
    load_plugins(namespace, namespace.PLUGINS)
