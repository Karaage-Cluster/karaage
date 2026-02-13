# Copyright 2012-2014 Brian May
#
# This file is part of python-tldap.
#
# python-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-tldap  If not, see <http://www.gnu.org/licenses/>.
from tldap.utils import DEFAULT_LDAP_ALIAS, ConnectionHandler


connections = None
"""An object containing a list of all LDAP connections."""


def setup(settings):
    """ Function used to initialize LDAP settings. """
    global connections
    connections = ConnectionHandler(settings)


# DatabaseWrapper.__init__() takes a dictionary, not a settings module, so
# we manually create the dictionary from the settings, passing only the
# settings that the database backends care about. Note that TIME_ZONE is used
# by the PostgreSQL backends.
# We load all these up for backwards compatibility, you should use
# connections['default'] instead.

class DefaultConnectionProxy(object):
    """
    Proxy for accessing the default DatabaseWrapper object's attributes. If you
    need to access the DatabaseWrapper object itself, use
    connections[DEFAULT_LDAP_ALIAS] instead.
    """
    def __getattr__(self, item):
        return getattr(connections[DEFAULT_LDAP_ALIAS], item)

    def __setattr__(self, name, value):
        return setattr(connections[DEFAULT_LDAP_ALIAS], name, value)

    def __delattr__(self, name):
        return delattr(connections[DEFAULT_LDAP_ALIAS], name)

    def __eq__(self, other):
        return connections[DEFAULT_LDAP_ALIAS] == other

    def __ne__(self, other):
        return connections[DEFAULT_LDAP_ALIAS] != other


""" The default LDAP connection. """
connection = DefaultConnectionProxy()
