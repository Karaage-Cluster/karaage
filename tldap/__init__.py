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

"""
Holds global stuff for tldap.

Q
    Shortcut to :py:class:`tldap.query_utils.Q`, allows combining query terms.

DEFAULT_LDAP_ALIAS
    Alias for default LDAP connection.
"""

from tldap.query_utils import Q  # noqa: F401


__author__ = """Brian May"""
__email__ = 'brian@linuxpenguins.xyz'
__version__ = '1.0.8'
