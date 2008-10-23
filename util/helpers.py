"""
Holds various helper methods
"""
__author__ = 'Sam Morrison'

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

import crypt
import random, string
from django_common.middleware.threadlocals import get_current_user
import datetime

from placard.connection import LDAPConnection
from placard.ldap_passwd import md5crypt

from karaage.machines.models import MachineCategory, UserAccount
from karaage.people.models import Person, Institute
from karaage.projects.models import Project

from accounts.ldap_utils.ldap_users import *

   

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

    

def check_password(password):
    """Return True if password valid"""
    if password.isdigit():
        return False
    
    if len(password) > 5:
        for i in password:
            if i.isdigit():
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
        if settings.DEBUG:
            print m
            print start
            print end
        if not m_end:
            m_end = end#datetime.date.today() - datetime.timedelta(days=1)
        if settings.DEBUG:
            print m_start   
            print m_end   
        if start >= m_end or m_start >= end:
            if settings.DEBUG:
                print '0'
            total += 0

        elif start < m_start and end > m_end:
            if settings.DEBUG:
                print '1'
            total += (m.no_cpus * ((m_end - m_start).days+1) * 24 * 60 * 60)
            
        elif end > m_end and start < m_start:
            if settings.DEBUG:
                print '2'
            total += (m.no_cpus * ((end - start).days+1) * 24 * 60 * 60)
        
        elif end > m_end:
            if settings.DEBUG:
                print '3'
            total += (m.no_cpus * ((m_end - start).days+1) * 24 * 60 * 60)

        elif start < m_start:
            if settings.DEBUG:
                print '4'
            total += (m.no_cpus * ((end - m_start).days+1) * 24 * 60 * 60)

        else:
            if settings.DEBUG:
                print '5'
            total += (m.no_cpus * ((end - start).days+1) * 24 * 60 * 60)
            
        #print '%s, %s' % (m, m_cpus)

            
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
