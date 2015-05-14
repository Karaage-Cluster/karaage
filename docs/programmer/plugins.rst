Plugins
=======
A plugin is a Django app with extra Karaage specific features. It can defined
extra settings, extra templates, extra URLS, and extra code.

For the purposes of this document, we assume the plugin is called kgplugin, and
defines a Django app with a python module called ``kgplugin``. You should
change this name.

Settings
--------
.. setting:: PLUGINS

PLUGINS
~~~~~~~
Default: ``[]`` (Empty list)

A list of classes that define Karaage plugins.

Creating a plugin
-----------------
.. py:module:: karaage.urls

A plugin needs to provide a urls.py file. This file can be empty if it doesn't
provide any urls. It can optionally provide values for ``urlpatterns`` and
``profile_urlpatterns``.

.. py:module:: karaage.plugins

A plugin needs to provide a plugin class that is derived from the
:py:class:`BasePlugin` class. It is configured with the
:setting:`PLUGINS` setting.

.. py:class:: BasePlugin

   Base class used for defining Karaage specific settings used to define
   plugins in Karaaage.

   .. versionchanged:: 3.1.5
 
      BasePlugin is derived from :py:class:`django.apps.AppConfig` if Django
      1.7 is detected.

Here is an example, taken from the karaage-usage pugin:

.. code-block:: python

   from karaage.plugins import BasePlugin

    class plugin(BasePlugin):
        name = "karaage.plugins.kgusage"
        django_apps = ("djcelery",)
        xmlrpc_methods = (
            ('karaage.plugins.kgusage.xmlrpc.parse_usage', 'parse_usage',),
        )
        settings = {
            'GRAPH_DEBUG': False,
            'GRAPH_DIR': 'kgusage/',
            'GRAPH_TMP': 'kgusage/',
        }
        depends = ("karaage.plugins.kgsoftware.plugin",)

The ``name`` value is required, all other attributes are optional.

The following attributes can be set:

.. py:attribute:: BasePlugin.name

   The python module for the Django app. This will be added to the
   :setting:`django:INSTALLED_APPS` Django setting.

   .. versionchanged:: 3.1.5

   If Django 1.7 is detected, the plugin class is added to
   :setting:`django:INSTALLED_APPS`, not this value. This setting is used
   by Django to locate the module.

.. py:attribute:: BasePlugin.django_apps

   A typle list of extra Django apps that are required for this plugin to work
   correctly. This will be added to the  :setting:`django:INSTALLED_APPS`
   setting.

.. py:attribute:: BasePlugin.xmlrpc_methods

   A tuple list of extra methods to add to the :setting:`XMLRPC_METHODS`
   setting.

.. py:attribute:: BasePlugin.settings

   A dictionary of extra settings, and default values. These are added to the
   Django settings. If the setting is already defined, the value given here is
   ignored.

.. py:attribute:: BasePlugin.depends

   A tuple list of plugins this plugin requires to be installed for it
   to operate correctly.

Templates
---------
The python module directory, can contain the ``templates`` directory. This
can have custom templates under the ``kgplugin`` directory. In addition,
Karaage will see the following extra files.

*  ``kgplugin/index_top.html``: contains HTML code to add to the top of the top
   level Karaage page.

*  ``kgplugin/index_bottom.html``: contains HTML code to add to the bottom of
   the top level Karaage page.

*  ``kgplugin/main_admin.html``: Links to add to the admin menu.

*  ``kgplugin/main_profile.html``: Links to add to the profile menu.

*  ``kgplugin/misc.html``: Links to add to the misc menu.

*  ``emails/email_footer.txt``: Footer to add to every outgoing email.

URLS
----
Extra URLS can be defined in the ``kgplugin.urls`` module, and should be called
``urlpatterns`` or ``profile_urlpatterns`` for URLS that should appear under
the profile directory.
