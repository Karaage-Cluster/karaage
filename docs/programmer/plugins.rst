Plugins
=======
A plugin is a Django app with extra Karaage specific features. It can defined
extra settings, extra templates, extra URLS, and extra code.

For the purposes of this document, we assume the plugin is called kgplugin, and
defines a Django app with a python module called ``kgplugin``. You should
change this name.

Configuring a plugin
--------------------
A plugin needs to provide a plugin class that is derived from the
:py:class:`BasePlugin` class.

.. py:class:: BasePlugin

   Base class used for defining Karaage specific settings used to define
   plugins in Karaaage

Here is an example, taken from the karaage-usage pugin:

.. code-block:: python

   from karaage.plugins import BasePlugin

    class plugin(BasePlugin):
        module = "kgusage"
        django_apps = ("djcelery",)
        xmlrpc_methods = (
            ('kgusage.xmlrpc.parse_usage', 'parse_usage',),
        )
        settings = {
            'GRAPH_DEBUG': False,
            'GRAPH_DIR': 'kgusage/',
            'GRAPH_TMP': 'kgusage/',
        }
        depends = ("kgsoftware.plugin",)

The ``module`` value is required, all other attributes are optional.

The following attributes can be set:

.. py:attribute:: BasePlugin.module

   The python module for the Django app. This will be added to
   ``INSTALLED_APPS`` Django configuration.

.. py:attribute:: BasePlugin.django_apps

   A typle list of extra Django apps that are required for this plugin to work
   correctly.

.. py:attribute:: BasePlugin.xmlrpc_methods

   A tuple list of extra methods to add to the ``XMLRPC_METHODS`` setting.

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
