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

"""
Holds various helper methods
"""
__author__ = 'Sam Morrison'

from django.contrib.auth.models import User

import datetime

from karaage.machines.models import MachineCategory, UserAccount


def check_username(username, machine_category):
    """Return True if username not taken and valid

    Keyword arguments:
    username -- username to check
    machine_category -- MachineCategory account is on
    
    """
    try:
        user = User.objects.get(username__exact=username)
    except:
        try:
            user_account = UserAccount.objects.get(username__exact=username, machine_category=machine_category, date_deleted__isnull=True)
        except:
            return True
        
    return False


def get_available_time(start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today(), machine_category=MachineCategory.objects.get_default()):
    """
    Calculates the total available time on a machine category for a given period
    Takes into account machines being commissioned and decommisioned
    """
    machines = machine_category.machine_set.all()
    total = 0
    
    for m in machines:
        m_start = m.start_date
        m_end = m.end_date
        if not m_end:
            m_end = end
        if start >= m_end or m_start >= end:
            total += 0
            
        elif start < m_start and end > m_end:
            total += (m.no_cpus * ((m_end - m_start).days) * 24 * 60 * 60)
            
        elif end > m_end and start < m_start:
            total += (m.no_cpus * ((end - start).days) * 24 * 60 * 60)
            
        elif end > m_end:
            total += (m.no_cpus * ((m_end - start).days) * 24 * 60 * 60)
            
        elif start < m_start:
            total += (m.no_cpus * ((end - m_start).days) * 24 * 60 * 60)
            
        else:
            total += (m.no_cpus * ((end - start).days) * 24 * 60 * 60)
            
    return total, get_ave_cpus(start, end, machine_category)
        

def get_ave_cpus(start, end, machine_category):
    cpus = 0.
    for m in machine_category.machine_set.all():
        m_start = m.start_date
        m_end = m.end_date

        if not m_end:
            m_end = datetime.date.today()
        if start >= m_end or end <= m_start:
            cpus += 0

        elif start < m_start and end > m_end:
            cpus += m.no_cpus * (m_end - m_start).days

        elif end > m_end:
            cpus += m.no_cpus * (m_end - start).days
            
        elif start < m_start:
            cpus += m.no_cpus * (end - m_start).days

        else:
            cpus += m.no_cpus * (end - start).days
            
    return cpus / (end-start).days
