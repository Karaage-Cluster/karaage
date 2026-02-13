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

""" This module provides the LDAP functions with transaction support faked,
with a subset of the functions from the real ldap module. """
import logging
import sys
from typing import Any, Callable, Dict, List, Optional

import ldap3
import six

import tldap.dn
import tldap.exceptions
import tldap.modlist

from .base import LdapBase


logger = logging.getLogger(__name__)


def _debug(*argv) -> None:
    argv = [str(arg) for arg in argv]
    logging.debug(" ".join(argv))


def raise_testfailure(place: str) -> None:
    raise tldap.exceptions.TestFailure("fail %s called" % place)


# errors

class NoSuchObject(Exception):
    pass


UpdateCallable = Callable[[ldap3.Connection], None]


# wrapper class

class LDAPwrapper(LdapBase):
    """ The LDAP connection class. """

    def __init__(self, settings_dict: dict) -> None:
        super(LDAPwrapper, self).__init__(settings_dict)
        self._transactions: List[List[UpdateCallable]] = []

    ####################
    # Cache Management #
    ####################

    def reset(self, force_flush_cache: bool = False) -> None:
        """
        Reset transaction back to original state, discarding all
        uncompleted transactions.
        """
        super(LDAPwrapper, self).reset()
        if len(self._transactions) == 0:
            raise RuntimeError("reset called outside a transaction.")
        self._transactions[-1] = []

    def _cache_get_for_dn(self, dn: str) -> Dict[str, bytes]:
        """
        Object state is cached. When an update is required the update will be
        simulated on this cache, so that rollback information can be correct.
        This function retrieves the cached data.
        """

        # no cached item, retrieve from ldap
        self._do_with_retry(
            lambda obj: obj.search(
                dn,
                '(objectclass=*)',
                ldap3.BASE,
                attributes=['*', '+']))
        results = self._obj.response
        if len(results) < 1:
            raise NoSuchObject("No results finding current value")
        if len(results) > 1:
            raise RuntimeError("Too many results finding current value")

        return results[0]['raw_attributes']

    ##########################
    # Transaction Management #
    ##########################

    def is_dirty(self) -> bool:
        """ Are there uncommitted changes? """
        if len(self._transactions) == 0:
            raise RuntimeError("is_dirty called outside a transaction.")
        if len(self._transactions[-1]) > 0:
            return True
        return False

    def is_managed(self) -> bool:
        """ Are we inside transaction management? """
        return len(self._transactions) > 0

    def enter_transaction_management(self) -> None:
        """ Start a transaction. """
        self._transactions.append([])

    def leave_transaction_management(self) -> None:
        """
        End a transaction. Must not be dirty when doing so. ie. commit() or
        rollback() must be called if changes made. If dirty, changes will be
        discarded.
        """
        if len(self._transactions) == 0:
            raise RuntimeError("leave_transaction_management called outside transaction")
        elif len(self._transactions[-1]) > 0:
            raise RuntimeError("leave_transaction_management called with uncommited rollbacks")
        else:
            self._transactions.pop()

    def commit(self) -> None:
        """
        Attempt to commit all changes to LDAP database. i.e. forget all
        rollbacks.  However stay inside transaction management.
        """
        if len(self._transactions) == 0:
            raise RuntimeError("commit called outside transaction")

        # If we have nested transactions, we don't actually commit, but push
        # rollbacks up to previous transaction.
        if len(self._transactions) > 1:
            for on_rollback in reversed(self._transactions[-1]):
                self._transactions[-2].insert(0, on_rollback)

        _debug("commit")
        self.reset()

    def rollback(self) -> None:
        """
        Roll back to previous database state. However stay inside transaction
        management.
        """
        if len(self._transactions) == 0:
            raise RuntimeError("rollback called outside transaction")

        _debug("rollback:", self._transactions[-1])
        # if something goes wrong here, nothing we can do about it, leave
        # database as is.
        try:
            # for every rollback action ...
            for on_rollback in self._transactions[-1]:
                # execute it
                _debug("--> rolling back", on_rollback)
                self._do_with_retry(on_rollback)
        except:  # noqa: E722
            _debug("--> rollback failed")
            exc_class, exc, tb = sys.exc_info()
            raise tldap.exceptions.RollbackError(
                "FATAL Unrecoverable rollback error: %r" % exc)
        finally:
            # reset everything to clean state
            _debug("--> rollback success")
            self.reset()

    def _process(self, on_commit: UpdateCallable, on_rollback: UpdateCallable) -> Any:
        """
        Process action. oncommit is a callback to execute action, onrollback is
        a callback to execute if the oncommit() has been called and a rollback
        is required
        """

        _debug("---> commiting", on_commit)
        result = self._do_with_retry(on_commit)

        if len(self._transactions) > 0:
            # add statement to rollback log in case something goes wrong
            self._transactions[-1].insert(0, on_rollback)

        return result

    ##################################
    # Functions needing Transactions #
    ##################################

    def add(self, dn: str, mod_list: dict) -> None:
        """
        Add a DN to the LDAP database; See ldap module. Doesn't return a result
        if transactions enabled.
        """

        _debug("add", self, dn, mod_list)

        # if rollback of add required, delete it
        def on_commit(obj):
            obj.add(dn, None, mod_list)

        def on_rollback(obj):
            obj.delete(dn)

        # process this action
        return self._process(on_commit, on_rollback)

    def modify(self, dn: str, mod_list: dict) -> None:
        """
        Modify a DN in the LDAP database; See ldap module. Doesn't return a
        result if transactions enabled.
        """

        _debug("modify", self, dn, mod_list)

        # need to work out how to reverse changes in mod_list; result in revlist
        revlist = {}

        # get the current cached attributes
        result = self._cache_get_for_dn(dn)

        # find the how to reverse mod_list (for rollback) and put result in
        # revlist. Also simulate actions on cache.
        for mod_type, l in six.iteritems(mod_list):
            for mod_op, mod_vals in l:

                _debug("attribute:", mod_type)
                if mod_type in result:
                    _debug("attribute cache:", result[mod_type])
                else:
                    _debug("attribute cache is empty")
                _debug("attribute modify:", (mod_op, mod_vals))

                if mod_vals is not None:
                    if not isinstance(mod_vals, list):
                        mod_vals = [mod_vals]

                if mod_op == ldap3.MODIFY_ADD:
                    # reverse of MODIFY_ADD is MODIFY_DELETE
                    reverse = (ldap3.MODIFY_DELETE, mod_vals)

                elif mod_op == ldap3.MODIFY_DELETE and len(mod_vals) > 0:
                    # Reverse of MODIFY_DELETE is MODIFY_ADD, but only if value
                    # is given if mod_vals is None, this means all values where
                    # deleted.
                    reverse = (ldap3.MODIFY_ADD, mod_vals)

                elif mod_op == ldap3.MODIFY_DELETE \
                        or mod_op == ldap3.MODIFY_REPLACE:
                    if mod_type in result:
                        # If MODIFY_DELETE with no values or MODIFY_REPLACE
                        # then we have to replace all attributes with cached
                        # state
                        reverse = (
                            ldap3.MODIFY_REPLACE,
                            tldap.modlist.escape_list(result[mod_type])
                        )
                    else:
                        # except if we have no cached state for this DN, in
                        # which case we delete it.
                        reverse = (ldap3.MODIFY_DELETE, [])

                else:
                    raise RuntimeError("mod_op of %d not supported" % mod_op)

                reverse = [reverse]
                _debug("attribute reverse:", reverse)
                if mod_type in result:
                    _debug("attribute cache:", result[mod_type])
                else:
                    _debug("attribute cache is empty")

                revlist[mod_type] = reverse

        _debug("--")
        _debug("mod_list:", mod_list)
        _debug("revlist:", revlist)
        _debug("--")

        # now the hard stuff is over, we get to the easy stuff
        def on_commit(obj):
            obj.modify(dn, mod_list)

        def on_rollback(obj):
            obj.modify(dn, revlist)

        return self._process(on_commit, on_rollback)

    def modify_no_rollback(self, dn: str, mod_list: dict):
        """
        Modify a DN in the LDAP database; See ldap module. Doesn't return a
        result if transactions enabled.
        """

        _debug("modify_no_rollback", self, dn, mod_list)
        result = self._do_with_retry(lambda obj: obj.modify_s(dn, mod_list))
        _debug("--")

        return result

    def delete(self, dn: str) -> None:
        """
        delete a dn in the ldap database; see ldap module. doesn't return a
        result if transactions enabled.
        """

        _debug("delete", self)

        # get copy of cache
        result = self._cache_get_for_dn(dn)

        # remove special values that can't be added
        def delete_attribute(name):
            if name in result:
                del result[name]
        delete_attribute('entryUUID')
        delete_attribute('structuralObjectClass')
        delete_attribute('modifiersName')
        delete_attribute('subschemaSubentry')
        delete_attribute('entryDN')
        delete_attribute('modifyTimestamp')
        delete_attribute('entryCSN')
        delete_attribute('createTimestamp')
        delete_attribute('creatorsName')
        delete_attribute('hasSubordinates')
        delete_attribute('pwdFailureTime')
        delete_attribute('pwdChangedTime')
        # turn into mod_list list.
        mod_list = tldap.modlist.addModlist(result)

        _debug("revlist:", mod_list)

        # on commit carry out action; on rollback restore cached state
        def on_commit(obj):
            obj.delete(dn)

        def on_rollback(obj):
            obj.add(dn, None, mod_list)

        return self._process(on_commit, on_rollback)

    def rename(self, dn: str, new_rdn: str, new_base_dn: Optional[str] = None) -> None:
        """
        rename a dn in the ldap database; see ldap module. doesn't return a
        result if transactions enabled.
        """

        _debug("rename", self, dn, new_rdn, new_base_dn)

        # split up the parameters
        split_dn = tldap.dn.str2dn(dn)
        split_newrdn = tldap.dn.str2dn(new_rdn)
        assert (len(split_newrdn) == 1)

        # make dn unqualified
        rdn = tldap.dn.dn2str(split_dn[0:1])

        # make newrdn fully qualified dn
        tmplist = [split_newrdn[0]]
        if new_base_dn is not None:
            tmplist.extend(tldap.dn.str2dn(new_base_dn))
            old_base_dn = tldap.dn.dn2str(split_dn[1:])
        else:
            tmplist.extend(split_dn[1:])
            old_base_dn = None
        newdn = tldap.dn.dn2str(tmplist)

        _debug("--> commit  ", self, dn, new_rdn, new_base_dn)
        _debug("--> rollback", self, newdn, rdn, old_base_dn)

        # on commit carry out action; on rollback reverse rename
        def on_commit(obj):
            obj.modify_dn(dn, new_rdn, new_superior=new_base_dn)

        def on_rollback(obj):
            obj.modify_dn(newdn, rdn, new_superior=old_base_dn)

        return self._process(on_commit, on_rollback)

    def fail(self) -> None:
        """ for testing purposes only. always fail in commit """

        _debug("fail")

        # on commit carry out action; on rollback reverse rename
        def on_commit(_obj):
            raise_testfailure("commit")

        def on_rollback(_obj):
            raise_testfailure("rollback")

        return self._process(on_commit, on_rollback)
