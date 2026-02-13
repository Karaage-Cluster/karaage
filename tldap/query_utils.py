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
from __future__ import absolute_import

import six

from .tree import Node


class Q(Node):
    """
    Encapsulates filters as objects that can then be combined logically
    (using ``&`` and ``|``).
    """
    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND

    def __init__(self, *args, **kwargs):
        super(Q, self).__init__(
            children=list(args) + list(six.iteritems(kwargs)))

    def _combine(self, other: 'Q', conn: str) -> 'Q':
        if not isinstance(other, Q):
            raise TypeError(other)
        if len(self.children) < 1:
            self.connector = conn
        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other: 'Q'):
        return self._combine(other, self.OR)

    def __and__(self, other: 'Q'):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj
