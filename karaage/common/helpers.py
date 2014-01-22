# Copyright 2007-2013 VPAC
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

"""
Holds various helper methods
"""
__author__ = 'Sam Morrison'

import datetime

from karaage.machines.models import MachineCategory, Account


def check_username(username, machine_category):
    """Return True if username not taken and valid

    Keyword arguments:
    username -- username to check
    machine_category -- MachineCategory account is on
    
    """
    try:
        Person.objects.get(username__exact=username)
    except:
        try:
            account = Account.objects.get(username__exact=username, machine_category=machine_category, date_deleted__isnull=True)
        except:
            return True
        
    return False


