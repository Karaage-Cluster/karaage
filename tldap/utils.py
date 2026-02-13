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

""" Contains ConnectionHandler which represents a list of connections. """

import sys
from threading import local


DEFAULT_LDAP_ALIAS = "default"


def load_backend(backend_name):
    __import__(backend_name)
    return sys.modules[backend_name]


class ConnectionHandler(object):
    """ Contains a list of known LDAP connections. """

    def __init__(self, databases):
        self.databases = databases
        self._connections = local()

    def __getitem__(self, alias):
        if hasattr(self._connections, alias):
            return getattr(self._connections, alias)

        db = self.databases[alias]

        backend = load_backend(db['ENGINE'])
        conn = backend.LDAPwrapper(db)
        setattr(self._connections, alias, conn)
        return conn

    def __iter__(self):
        return iter(self.databases)

    def all(self):
        """ Return list of all connections. """
        return [self[alias] for alias in self]
