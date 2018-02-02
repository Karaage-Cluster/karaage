# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django_xmlrpc.decorators import xmlrpc_func

from karaage.machines.models import Account


@xmlrpc_func(returns='int', args=['string', 'string'])
def get_disk_quota(username, machine_name=None):
    """
    Returns disk quota for username in KB
    """

    try:
        ua = Account.objects.get(
            username=username,
            date_deleted__isnull=True)
    except Account.DoesNotExist:
        return 'Account not found'

    result = ua.get_disk_quota()
    if result is None:
        return False

    return result * 1048576
