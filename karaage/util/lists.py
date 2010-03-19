# Copyright 2007-2010 VPAC
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

from andsome.util import unique

from karaage.people.models import Person
from karaage.machines.models import MachineCategory

def get_ml_vpac_users():
    mc = MachineCategory.objects.get(name='VPAC')
    emails = []
    for u in Person.active.all():
        if not u.is_locked():
            if u.has_account(mc):
                if u.email:
                    if u.email != 'unknown@vpac.org':
                        emails.append(u.email)
                        
    emails = unique(emails)
    emails.sort()
    
    return emails
