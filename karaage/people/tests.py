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
from karaage.machines.models import UserAccount
from karaage.test_data.initial_ldap_data import test_ldif

class UserTestCase(TestCase):

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        base = server.get_dn_suffix()
        server.ldapadd("\n".join(test_ldif)+"\n")

        self.server = server

    def tearDown(self):
        self.server.stop()


    def test_admin_create_user_with_account(self):

        users = Person.objects.count()
        project = Project.objects.get(pid='TestProject1')
        p_users = project.users.count()
        logged_in = self.client.login(username='super', password='aq12ws')
        self.failUnlessEqual(logged_in, True)

        response = self.client.get(reverse('kg_add_user'))
        self.failUnlessEqual(response.status_code, 200)
        
        form_data = {
            'title' : 'Mr',
            'first_name': 'Sam',
            'last_name': 'Morrison',
            'position': 'Sys Admin',
            'institute': 1,
            'department': 'eddf',
            'email': 'sam@vpac.org',
            'country': 'AU',
            'telephone': '4444444',
            'username': 'samtest',
            'password1': 'Exaiquouxei0',
            'password2': 'Exaiquouxei0',
            'project': 'TestProject1',
            'needs_account': True,
            'machine_category': 1,
        }

        response = self.client.post(reverse('kg_add_user'), form_data)
        self.failUnlessEqual(response.status_code, 302)

        self.assertEqual(Person.objects.count(), users+1)
        users = users + 1
        person = Person.objects.get(pk=users)
        self.assertEqual(person.is_active, True)
        self.assertEqual(person.user.username, 'samtest')
        self.assertEqual(UserAccount.objects.count(), 2)
        self.assertEqual(project.users.count(), p_users+1)
        lcon = LDAPClient()
        luser = lcon.get_user('uid=samtest')
        self.assertEqual(luser.givenName, 'Sam')
        self.assertEqual(luser.objectClass, settings.ACCOUNT_OBJECTCLASS)
        
     
    def stest_admin_create_user(self):

        users = Person.objects.count()
        project = Project.objects.get(pid='TestProject1')
        p_users = project.users.count()
        logged_in = self.client.login(username='super', password='secret')
        self.failUnlessEqual(logged_in, True)
        response = self.client.get(reverse('kg_add_user'))
        
        self.failUnlessEqual(response.status_code, 200)

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

        response = self.client.post(reverse('kg_add_user'), form_data)
        self.failUnlessEqual(response.status_code, 302)

        self.assertEqual(Person.objects.count(), users+1)
        users = users + 1
        person = Person.objects.get(pk=users)
        self.assertEqual(person.is_active, True)
        self.assertEqual(person.user.username, 'samtest2')
        lcon = LDAPClient()
        luser = lcon.get_user('uid=samtest2')
        self.assertEqual(luser.givenName, 'Sam')
        self.assertEqual(luser.objectClass, settings.USER_OBJECTCLASS)
        # Try adding it again - Should fail
        response = self.client.post(reverse('kg_add_user'), form_data)
        self.failUnlessEqual(response.status_code, 200)

    def stest_delete_activate_user(self):
        logged_in = self.client.login(username='super', password='secret')
        user = Person.objects.get(user__username='kgtestuser3')
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.project_set.count(), 1)
        self.assertEqual(user.useraccount_set.count(), 1)
        self.assertEqual(user.useraccount_set.all()[0].date_deleted, None)
        lcon = LDAPClient()
        luser = lcon.get_user('uid=kgtestuser3')
        self.assertEqual(luser.givenName, 'Test')

        response = self.client.get(reverse('admin_delete_user', args=[user.username]))
        self.failUnlessEqual(response.status_code, 200)
        # Test deleting
        response = self.client.post(reverse('admin_delete_user', args=[user.username]))
        self.failUnlessEqual(response.status_code, 302)
        
        user = Person.objects.get(user__username='kgtestuser3')

        self.assertEqual(user.is_active, False)
        self.assertEqual(user.project_set.count(), 0)
        self.assertEqual(user.useraccount_set.count(), 1)
        self.assertEqual(user.useraccount_set.all()[0].date_deleted, datetime.date.today())
        self.failUnlessRaises(placard_exceptions.DoesNotExistException, lcon.get_user, 'uid=kgtestuser3')

        # Test activating
        response = self.client.post(reverse('admin_activate_user', args=[user.username]))
        self.failUnlessEqual(response.status_code, 302)
        user = Person.objects.get(user__username='kgtestuser3')
        self.assertEqual(user.is_active, True)
        luser = lcon.get_user('uid=kgtestuser3')
        self.assertEqual(luser.givenName, 'Test')
        
    def stest_remove_from_project(self):
        user = Person.objects.get(pk=Person.objects.count())

    def stest_delete_user_account(self):
        user = Person.objects.get(pk=Person.objects.count())
        ua = user.useraccount_set.all()[0]
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.useraccount_set.count(), 1)
        self.assertEqual(ua.date_deleted, None)

        response = self.client.post('/%susers/accounts/delete/%i/' % (settings.BASE_URL, ua.id))
        self.failUnlessEqual(response.status_code, 302)
        
        user = Person.objects.get(pk=Person.objects.count())
        ua = user.useraccount_set.all()[0]
        self.assertEqual(ua.date_deleted, datetime.date.today())
        self.assertEqual(user.project_set.count(), 0)

    def stest_default_projects(self):

        user = Person.objects.get(pk=Person.objects.count())
        ua = user.useraccount_set.all()[0]

        self.assertEqual(user.project_set.count(), 1)
        self.assertEqual(user.project_set.all()[0], ua.default_project)
        project = Project.objects.create(
            pid='test2',
            name='test project',
            leader=user,
            start_date = datetime.date.today(),
            machine_category=MachineCategory.objects.get(name='VPAC'),
            institute=Institute.objects.get(name='VPAC'),
            is_active=True,
            is_expertise=True,
            is_approved=True,
        )
        project.users.add(user)
        self.assertEqual(user.project_set.count(), 2)
        # change default
        response = self.client.post(reverse('admin_make_default', args=[ua.id, project.pid]))
        
        self.failUnlessEqual(response.status_code, 302)

        user = Person.objects.get(pk=Person.objects.count())
        ua = user.useraccount_set.all()[0]
        project = Project.objects.get(pk='test2')
       
        self.assertEqual(user.project_set.count(), 2)
        self.assertEqual(project, ua.default_project)

       
    def stest_add_user_to_project(self):

        user = Person.objects.get(pk=Person.objects.count())
        ua = user.useraccount_set.all()[0]

        self.assertEqual(user.project_set.count(), 1)

        project = Project.objects.create(
            pid='test2',
            name='test project 5',
            leader=Person.objects.get(user__username='leader'),
            start_date = datetime.date.today(),
            machine_category=MachineCategory.objects.get(name='VPAC'),
            institute=Institute.objects.get(name='VPAC'),
            is_active=True,
            is_expertise=True,
            is_approved=True,
        )

        response = self.client.post(reverse('kg_user_detail', args=[user.username]), { 'project': 'test2', 'project-add': 'true' })
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(user.project_set.count(), 2)


    def stest_approve_account(self):
        u = User.objects.create_user('dummy2', 'sam@vpac.org', 'aq12ws')
        u.is_active = False
        u.save()
        user = Person.objects.create(
            user=u,
            first_name='approve',
            last_name='Test',
            title='Mr',
            institute=Institute.objects.get(name='VPAC'),
            country='AU',
        )
        project = Project.objects.get(pk='test')
        ur = ProjectJoinRequest.objects.create(
            person=user,
            project=project,
            machine_category=MachineCategory.objects.get(name='VPAC'),
            leader_approved=True,
            needs_account=True,
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(project.users.count(), 1)
        self.assertEqual(user.useraccount_set.count(), 0)
        
        response = self.client.get(reverse('admin_account_approve', args=[ur.id]))
        self.failUnlessEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 2)
        
        user = Person.objects.get(user__username='dummy2')
        project = Project.objects.get(pk='test')
        
        self.assertEqual(user.is_active, True)
        self.assertEqual(project.users.count(), 2)
        self.assertEqual(user.useraccount_set.count(), 1)
