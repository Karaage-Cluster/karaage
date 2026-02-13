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

""" This module provides the LDAP functions with transaction support disabled,
with a subset of the functions from the real ldap module. """
from typing import Optional

from .base import LdapBase


# wrapper class

class LDAPwrapper(LdapBase):
    """ The LDAP connection class. """

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
        return False

    def is_managed(self) -> bool:
        """ Are we inside transaction management? """
        return False

    def enter_transaction_management(self) -> None:
        """ Start a transaction. """
        pass

    def leave_transaction_management(self) -> None:
        """
        End a transaction. Must not be dirty when doing so. ie. commit() or
        rollback() must be called if changes made. If dirty, changes will be
        discarded.
        """
        pass

    def commit(self) -> None:
        """
        Attempt to commit all changes to LDAP database. i.e. forget all
        rollbacks.  However stay inside transaction management.
        """
        pass

    def rollback(self) -> None:
        """
        Roll back to previous database state. However stay inside transaction
        management.
        """
        pass

    ##################################
    # Functions needing Transactions #
    ##################################

    def add(self, dn: str, mod_list: dict) -> None:
        """
        Add a DN to the LDAP database; See ldap module. Doesn't return a result
        if transactions enabled.
        """

        return self._do_with_retry(lambda obj: obj.add_s(dn, mod_list))

    def modify(self, dn: str, mod_list: dict) -> None:
        """
        Modify a DN in the LDAP database; See ldap module. Doesn't return a
        result if transactions enabled.
        """

        return self._do_with_retry(lambda obj: obj.modify_s(dn, mod_list))

    def modify_no_rollback(self, dn: str, mod_list: dict) -> None:
        """
        Modify a DN in the LDAP database; See ldap module. Doesn't return a
        result if transactions enabled.
        """

        return self._do_with_retry(lambda obj: obj.modify_s(dn, mod_list))

    def delete(self, dn: str) -> None:
        """
        delete a dn in the ldap database; see ldap module. doesn't return a
        result if transactions enabled.
        """

        return self._do_with_retry(lambda obj: obj.delete_s(dn))

    def rename(self, dn: str, new_rdn: str, new_base_dn: Optional[str] = None) -> None:
        """
        rename a dn in the ldap database; see ldap module. doesn't return a
        result if transactions enabled.
        """

        return self._do_with_retry(
            lambda obj: obj.rename_s(dn, new_rdn, new_base_dn))
