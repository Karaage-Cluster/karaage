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

""" This module provides the LDAP base functions
with a subset of the functions from the real ldap module. """

import logging
import ssl
from typing import Callable, Generator, Optional, Tuple, TypeVar
from urllib.parse import urlparse

import ldap3
import ldap3.core.exceptions as exceptions


logger = logging.getLogger(__name__)


def _debug(*argv):
    argv = [str(arg) for arg in argv]
    logger.debug(" ".join(argv))


Entity = TypeVar('Entity')


class LdapBase(object):
    """ The vase LDAP connection class. """

    def __init__(self, settings_dict: dict) -> None:
        self.settings_dict = settings_dict
        self._obj = None
        self._connection_class = ldap3.Connection

    def close(self) -> None:
        if self._obj is not None:
            self._obj.unbind()
            self._obj = None

    #########################
    # Connection Management #
    #########################

    def set_connection_class(self, connection_class):
        self._connection_class = connection_class

    def check_password(self, dn: str, password: str) -> bool:
        try:
            conn = self._connect(user=dn, password=password)
            conn.unbind()
            return True
        except exceptions.LDAPInvalidCredentialsResult:
            return False
        except exceptions.LDAPUnwillingToPerformResult:
            return False

    def _connect(self, user: str, password: str) -> ldap3.Connection:
        settings = self.settings_dict

        _debug("connecting")
        url = urlparse(settings['URI'])

        if url.scheme == "ldaps":
            use_ssl = True
        elif url.scheme == "ldap":
            use_ssl = False
        else:
            raise RuntimeError("Unknown scheme '%s'" % url.scheme)

        if ":" in url.netloc:
            host, port = url.netloc.split(":")
            port = int(port)
        else:
            host = url.netloc
            if use_ssl:
                port = 636
            else:
                port = 389

        start_tls = False
        if 'START_TLS' in settings and settings['START_TLS']:
            start_tls = True

        tls = None
        if use_ssl or start_tls:
            tls = ldap3.Tls()

            if 'CIPHERS' in settings:
                tls.ciphers = settings['CIPHERS']

            if 'TLS_CA' in settings and settings['TLS_CA']:
                tls.ca_certs_file = settings['TLS_CA']

            if 'REQUIRE_TLS' in settings and settings['REQUIRE_TLS']:
                tls.validate = ssl.CERT_REQUIRED

        s = ldap3.Server(host, port=port, use_ssl=use_ssl, tls=tls)
        c = self._connection_class(
            s,  # client_strategy=ldap3.STRATEGY_SYNC_RESTARTABLE,
            user=user, password=password, authentication=ldap3.SIMPLE)
        c.strategy.restartable_sleep_time = 0
        c.strategy.restartable_tries = 1
        c.raise_exceptions = True

        c.open()

        if start_tls:
            c.start_tls()

        try:
            c.bind()
        except:  # noqa: E722
            c.unbind()
            raise

        return c

    def _reconnect(self) -> None:
        settings = self.settings_dict
        try:
            self._obj = self._connect(
                user=settings['USER'], password=settings['PASSWORD'])
        except Exception:
            self._obj = None
            raise
        assert self._obj is not None

    def _do_with_retry(self, fn: Callable[[ldap3.Connection], Entity]) -> Entity:
        if self._obj is None:
            self._reconnect()
            assert self._obj is not None

        try:
            return fn(self._obj)
        except ldap3.core.exceptions.LDAPSessionTerminatedByServerError:
            # if it fails, reconnect then retry
            _debug("SERVER_DOWN, reconnecting")
            self._reconnect()
            return fn(self._obj)

    ###################
    # read only stuff #
    ###################

    def search(self, base, scope, filterstr='(objectClass=*)',
               attrlist=None, limit=None) -> Generator[Tuple[str, dict], None, None]:
        """
        Search for entries in LDAP database.
        """

        _debug("search", base, scope, filterstr, attrlist, limit)

        # first results
        if attrlist is None:
            attrlist = ldap3.ALL_ATTRIBUTES
        elif isinstance(attrlist, set):
            attrlist = list(attrlist)

        def first_results(obj):
            _debug("---> searching ldap", limit)
            obj.search(
                base, filterstr, scope, attributes=attrlist, paged_size=limit)
            return obj.response

        # get the 1st result
        result_list = self._do_with_retry(first_results)

        # Loop over list of search results
        for result_item in result_list:
            # skip searchResRef for now
            if result_item['type'] != "searchResEntry":
                continue
            dn = result_item['dn']
            attributes = result_item['raw_attributes']
            # did we already retrieve this from cache?
            _debug("---> got ldap result", dn)
            _debug("---> yielding", result_item)
            yield (dn, attributes)

        # we are finished - return results, eat cake
        _debug("---> done")
        return

    ####################
    # Cache Management #
    ####################

    def reset(self, force_flush_cache: bool = False) -> None:
        """
        Reset transaction back to original state, discarding all
        uncompleted transactions.
        """
        pass

    ##########################
    # Transaction Management #
    ##########################

    # Fake it

    def is_dirty(self) -> bool:
        """ Are there uncommitted changes? """
        raise NotImplementedError()

    def is_managed(self) -> bool:
        """ Are we inside transaction management? """
        raise NotImplementedError()

    def enter_transaction_management(self) -> None:
        """ Start a transaction. """
        raise NotImplementedError()

    def leave_transaction_management(self) -> None:
        """
        End a transaction. Must not be dirty when doing so. ie. commit() or
        rollback() must be called if changes made. If dirty, changes will be
        discarded.
        """
        raise NotImplementedError()

    def commit(self) -> None:
        """
        Attempt to commit all changes to LDAP database. i.e. forget all
        rollbacks.  However stay inside transaction management.
        """
        raise NotImplementedError()

    def rollback(self) -> None:
        """
        Roll back to previous database state. However stay inside transaction
        management.
        """
        raise NotImplementedError()

    ##################################
    # Functions needing Transactions #
    ##################################

    def add(self, dn: str, mod_list: dict) -> None:
        """
        Add a DN to the LDAP database; See ldap module. Doesn't return a result
        if transactions enabled.
        """
        raise NotImplementedError()

    def modify(self, dn: str, mod_list: dict) -> None:
        """
        Modify a DN in the LDAP database; See ldap module. Doesn't return a
        result if transactions enabled.
        """
        raise NotImplementedError()

    def modify_no_rollback(self, dn: str, mod_list: dict) -> None:
        """
        Modify a DN in the LDAP database; See ldap module. Doesn't return a
        result if transactions enabled.
        """
        raise NotImplementedError()

    def delete(self, dn: str) -> None:
        """
        delete a dn in the ldap database; see ldap module. doesn't return a
        result if transactions enabled.
        """
        raise NotImplementedError()

    def rename(self, dn: str, new_rdn: str, new_base_dn: Optional[str] = None) -> None:
        """
        rename a dn in the ldap database; see ldap module. doesn't return a
        result if transactions enabled.
        """
        raise NotImplementedError()
