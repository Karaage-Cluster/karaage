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
from django.conf import settings

import random, string
import datetime

from placard.ldap_passwd import md5crypt

from karaage.machines.models import MachineCategory, UserAccount
from karaage.projects.models import Project


def create_password_hash(raw_password):
    return '{crypt}%s' % md5crypt(raw_password)


def _getsalt(chars=string.letters + string.digits):
    """generate a random 2-character 'salt'"""
    return random.choice(chars) + random.choice(chars)


def get_new_pid(institute, is_expertise):
    """ Return a new Project ID

    Keyword arguments:
    institute_id -- Institute id
    ia_expertise -- is project an expertise
    
    """
    no = 1
    number = '0001'
    if is_expertise:
        prefix = 'eppn%s' % institute.name.replace(' ', '')[:4]
    else:
        prefix = 'p%s' % institute.name.replace(' ', '')[:4]

    found = True
    while found:
        try:
            project = Project.objects.get(pid=prefix+number)
            number = str(int(number) + 1)
            if len(number) == 1:
                number = '000' + number
            elif len(number) == 2:
                number = '00' + number
            elif len(number) == 3:
                number = '0' + number
        except:
            found = False    
    
    return prefix+number


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

    

def check_password(password, old_password=None):
    """Return True if password valid"""
    from crack import VeryFascistCheck
    try:
        VeryFascistCheck(password, old=old_password)
    except:
	return False

    return True


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
            m_end = end#datetime.date.today() - datetime.timedelta(days=1)
        if start >= m_end or m_start >= end:
            total += 0

        elif start < m_start and end > m_end:
            total += (m.no_cpus * ((m_end - m_start).days+1) * 24 * 60 * 60)
            
        elif end > m_end and start < m_start:
            total += (m.no_cpus * ((end - start).days+1) * 24 * 60 * 60)
        
        elif end > m_end:
            total += (m.no_cpus * ((m_end - start).days+1) * 24 * 60 * 60)

        elif start < m_start:
            total += (m.no_cpus * ((end - m_start).days+1) * 24 * 60 * 60)

        else:
            total += (m.no_cpus * ((end - start).days+1) * 24 * 60 * 60)
            
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
