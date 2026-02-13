# Copyright 2018 Brian May
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
from typing import Dict, Iterator, Optional, Set, Tuple

import ldap3
from ldap3.core.exceptions import LDAPNoSuchObjectResult

import tldap
import tldap.fields
from tldap.backend.base import LdapBase
from tldap.filter import filter_format


def get_filter_item(name: str, operation: bytes, value: bytes) -> bytes:
    """
    A field could be found for this term, try to get filter string for it.
    """
    assert isinstance(name, str)
    assert isinstance(value, bytes)
    if operation is None:
        return filter_format(b"(%s=%s)", [name, value])
    elif operation == "contains":
        assert value != ""
        return filter_format(b"(%s=*%s*)", [name, value])
    else:
        raise ValueError("Unknown search operation %s" % operation)


def get_filter(q: tldap.Q, fields: Dict[str, tldap.fields.Field], pk: str):
    """
    Translate the Q tree into a filter string to search for, or None
    if no results possible.
    """
    # check the details are valid
    if q.negated and len(q.children) == 1:
        op = b"!"
    elif q.connector == tldap.Q.AND:
        op = b"&"
    elif q.connector == tldap.Q.OR:
        op = b"|"
    else:
        raise ValueError("Invalid value of op found")

    # scan through every child
    search = []
    for child in q.children:
        # if this child is a node, then descend into it
        if isinstance(child, tldap.Q):
            search.append(get_filter(child, fields, pk))
        else:
            # otherwise get the values in this node
            name, value = child

            # split the name if possible
            name, _, operation = name.rpartition("__")
            if name == "":
                name, operation = operation, None

            # replace pk with the real attribute
            if name == "pk":
                name = pk

            # DN is a special case
            if name == "dn":
                dn_name = "entryDN:"
                if isinstance(value, list):
                    s = []
                    for v in value:
                        assert isinstance(v, str)
                        v = v.encode('utf_8')
                        s.append(get_filter_item(dn_name, operation, v))
                    search.append("(&".join(search) + ")")

                # or process just the single value
                else:
                    assert isinstance(value, str)
                    v = value.encode('utf_8')
                    search.append(get_filter_item(dn_name, operation, v))
                continue

            # try to find field associated with name
            field = fields[name]
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
                assert isinstance(value, str)

            # process as list
            if isinstance(value, list):
                s = []
                for v in value:
                    v = field.value_to_filter(v)
                    s.append(get_filter_item(name, operation, v))
                search.append(b"(&".join(search) + b")")

            # or process just the single value
            else:
                value = field.value_to_filter(value)
                search.append(get_filter_item(name, operation, value))

    # output the results
    if len(search) == 1 and not q.negated:
        # just one non-negative term, return it
        return search[0]
    else:
        # multiple terms
        return b"(" + op + b"".join(search) + b")"


def _get_search_params(query: Optional[tldap.Q], fields: Dict[str, tldap.fields.Field],
                       object_classes: Set[str], pk: str):
    # add object classes to search array
    oc_query = tldap.Q()
    for oc in sorted(object_classes):
        oc_query = oc_query & tldap.Q(objectClass=oc)

    if query is None:
        query = oc_query
    else:
        query = oc_query & query

    # do a SUBTREE search
    scope = ldap3.SUBTREE

    # construct search filter string
    if query is not None:
        search_filter = get_filter(query, fields, pk)
    else:
        search_filter = None

    return scope, search_filter


def search(
        connection: LdapBase, query: Optional[tldap.Q], fields: Dict[str, tldap.fields.Field],
        base_dn: str, object_classes: Set[str], pk: str) -> Iterator[Tuple[str, dict]]:
    field_names = list(fields.keys())

    scope, search_filter = _get_search_params(query, fields, object_classes, pk)

    try:
        results = connection.search(base_dn, scope, search_filter, field_names)
        for result in results:
            dn = result[0]
            data = result[1]
            yield dn, data
    except LDAPNoSuchObjectResult:
        pass
