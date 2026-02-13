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

""" Transaction middleware for Django. """

from django.utils.deprecation import MiddlewareMixin

import tldap.transaction


class TransactionMiddleware(MiddlewareMixin):
    """
    Transaction middleware. If this is enabled, each view function will be run
    with commit_on_response activated - that way a save() doesn't do a direct
    commit, the commit is done when a successful response is created. If an
    exception happens, the database is rolled back.
    """
    def process_request(self, request):
        """Enters transaction management"""
        tldap.transaction.enter_transaction_management()

    def process_exception(self, request, exception):
        """Rolls back the database and leaves transaction management"""
        tldap.transaction.rollback()

    def process_response(self, request, response):
        """Commits and leaves transaction management."""
        if tldap.transaction.is_managed():
            tldap.transaction.commit()
            tldap.transaction.leave_transaction_management()
        return response
