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

from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

import datetime
from time import sleep
from placard.server import slapd
from placard.client import LDAPClient
from placard import exceptions as placard_exceptions

from karaage.people.models import Person, Institute
from karaage.projects.models import Project
from karaage.machines.models import UserAccount, MachineCategory, Machine
from karaage.test_data.initial_ldap_data import test_ldif

class UserAccountTestCase(TestCase):

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()
        server.ldapadd("\n".join(test_ldif)+"\n")

        self.server = server
        form_data = {
            'title' : 'Mr',
            'first_name': 'Sam',
            'last_name': 'Morrison2',
            'position': 'Sys Admin',
            'institute': 1,
            'department': 'eddf',
            'email': 'sam@vpac.org',
            'country': 'AU',
            'telephone': '4444444',
            'username': 'samtest2',
            'password1': 'Exaiquouxei0',
            'password2': 'Exaiquouxei0',
            'needs_account': False,
            }
        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.post(reverse('kg_add_user'), form_data)
        self.failUnlessEqual(response.status_code, 302)


    def tearDown(self):
        self.server.stop()

    def test_add_useraccount(self):

        response = self.client.get(reverse('kg_add_useraccount', args=['samtest2']))
        self.failUnlessEqual(response.status_code, 200)
        
        form_data = {
            'username': 'samtest2',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }
            
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.failUnlessEqual(response.status_code, 302)
        person = Person.objects.get(user__username="samtest2")
        lcon = LDAPClient()
        luser = lcon.get_user('uid=samtest2')
        self.assertEqual(luser.objectClass, settings.ACCOUNT_OBJECTCLASS)
        self.assertTrue(person.has_account(MachineCategory.objects.get(pk=1)))

    def test_add_useraccount_different_username(self):

        response = self.client.get(reverse('kg_add_useraccount', args=['samtest2']))
        self.failUnlessEqual(response.status_code, 200)
        
        form_data = {
            'username': 'samtest77',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }
            
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.failUnlessEqual(response.status_code, 302)
        person = Person.objects.get(user__username="samtest2")
        lcon = LDAPClient()
        luser = lcon.get_user('uid=samtest77')
        self.assertEqual(luser.objectClass, settings.ACCOUNT_OBJECTCLASS)
        self.assertTrue(person.has_account(MachineCategory.objects.get(pk=1)))


    def test_fail_add_useraccounts_username(self):
        form_data = {
            'username': 'samtest2',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }          
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.failUnlessEqual(response.status_code, 302)
        
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.assertContains(response, "Username already in use")

    def test_fail_add_useraccounts_username(self):
        form_data = {
            'username': 'samtest2',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }          
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.failUnlessEqual(response.status_code, 302)
        
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.assertContains(response, "Username already in use")


    def test_fail_add_useraccounts_project(self):
        form_data = {
            'username': 'samtest2',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }          
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.failUnlessEqual(response.status_code, 302)

        form_data = {
            'username': 'samtest2',
            'machine_category': 2,
            'default_project': 'TestProject1',
            }

        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.assertContains(response, "Default project not in machine category")


    def test_fail_add_useraccounts_mc(self):
        form_data = {
            'username': 'samtest2',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }          
        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.failUnlessEqual(response.status_code, 302)

        form_data = {
            'username': 'samtest3',
            'machine_category': 1,
            'default_project': 'TestProject1',
            }

        response = self.client.post(reverse('kg_add_useraccount', args=['samtest2']), form_data)
        self.assertContains(response, "Default project not in machine category")



class MachineTestCase(TestCase):

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()
        server.ldapadd("\n".join(test_ldif)+"\n")

        self.server = server
        today = datetime.datetime.now()
        # 10cpus
        mach1 = Machine.objects.get(pk=1)
        mach1.start_date = today - datetime.timedelta(days=100)
        mach1.save()
        # 40 cpus
        mach2 = Machine.objects.get(pk=2)
        mach2.start_date = today - datetime.timedelta(days=100)
        mach2.end_date = today - datetime.timedelta(days=20)
        mach2.save()
        # 8000 cpus
        mach3 = Machine.objects.get(pk=3)
        mach3.start_date = today - datetime.timedelta(days=30)
        mach3.save()

    def tearDown(self):
        self.server.stop()

    def test_available_time(self):
        from karaage.util.helpers import get_available_time
        mc1 = MachineCategory.objects.get(pk=1)
        mc2 = MachineCategory.objects.get(pk=2)
        day = 60*60*24
        available_time, avg_cpus = get_available_time(machine_category=mc1)

        self.failUnlessEqual(avg_cpus, 10)
        self.failUnlessEqual(available_time, 90*day*avg_cpus)
        self.failUnlessEqual(available_time, 90*day*10)

        available_time, avg_cpus = get_available_time(machine_category=mc2)

        self.failUnlessEqual(avg_cpus, 2697.7777777777778)
        self.failUnlessEqual(available_time, 90*day*avg_cpus)
        self.failUnlessEqual(available_time, (40*(70*day))+(8000*(30*day)))
