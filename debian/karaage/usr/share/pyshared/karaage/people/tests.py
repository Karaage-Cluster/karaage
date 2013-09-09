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
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management import call_command

import datetime
from tldap.test import slapd

from karaage.people.models import Person, Institute, InstituteDelegate
from karaage.projects.models import Project
from karaage.machines.models import UserAccount, MachineCategory
from karaage.test_data.initial_ldap_data import test_ldif

from karaage.datastores import ldap_schemas

class UserTestCase(TestCase):

    def setUp(self):
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        call_command('loaddata', 'karaage_data', **{'verbosity': 0})

        self.server = server

    def tearDown(self):
        self.server.stop()


    def do_permission_tests(self, test_object, users):
        for user_id in users:
#            print "can user '%d' access '%s'?"%(user_id, test_object)
            user = User.objects.get(id=user_id)
            result = test_object.can_view(user)
            expected_result = users[user_id]
#            print "---> got:'%s' expected:'%s'"%(result, expected_result)
            self.failUnlessEqual(result, expected_result)
#            print

    def test_permissions(self):
        test_object = Project.objects.get(pid="TestProject1")
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate, project leader
            2: False, # person 2 cannot view
            3: True, # person 3 can view: project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=1)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: self, project member, person's institute delegate
            2: False, # person 2 cannot view
            3: False, # person 3 cannot view
            4: True, # person 4 can view: is_staff, institute delegate
        })

        test_object = Person.objects.get(id=2)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate
            2: True, # person 2 can view: self
            3: False, # person 3 cannot view
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=3)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate, project leader
            2: False, # person 2 cannot view
            3: True, # person 3 can view: self, project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=4)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate
            2: False, # person 2 cannot view
            3: False, # person 3 cannot view
            4: True, # person 4 can view: self, is_staff
        })

        # add user 2 to project
        # test that members can see other people in own project
#        print "-------------------------------------------------------------------"
        project = Project.objects.get(pid="TestProject1")
        project.users=[2,3]

        test_object = Project.objects.get(pid="TestProject1")
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate
            2: True, # person 2 can view: project member
            3: True, # person 3 can view: project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=1)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view:  self, project member, delegate of institute
            2: False, # person 2 cannot view
            3: False, # person 3 cannot view
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=2)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate, project leader
            2: True, # person 2 can view: self
            3: True, # person 3 can view: project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=3)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate, project leader
            2: True, # person 2 can view: project member
            3: True, # person 3 can view: self, project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=4)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate
            2: False, # person 2 cannot view
            3: False, # person 3 cannot view
            4: True, # person 4 can view: self, is_staff
        })

        # change institute of all people
        # Test institute leader can access people in project despite not being
        # institute leader for these people.
#        print "-------------------------------------------------------------------"
        Person.objects.all().update(institute=2)
        #Institute.objects.filter(pk=2).update(delegate=2,active_delegate=2)
        InstituteDelegate.objects.get_or_create(institute=Institute.objects.get(id=2), person=Person.objects.get(id=2))
        project = Project.objects.get(pid="TestProject1")
        project.leaders=[2]

        test_object = Project.objects.get(pid="TestProject1")
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate
            2: True, # person 2 can view: project member, person's institute delegate, project leader
            3: True, # person 3 can view: project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=1)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: self, project member
            2: True, # person 2 can view: person's institute delegate
            3: False, # person 3 cannot view
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=2)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: project's institute leader
            2: True, # person 2 can view: self, person's institute delegate, project leader
            3: True, # person 3 can view: project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=3)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: project's institute leader
            2: True, # person 2 can view: project member, person's institute delegate, project leader
            3: True, # person 3 can view: self, project member
            4: True, # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=4)
        self.do_permission_tests(test_object, {
            1: True, # person 1 can view: person's institute delegate
            2: True, # person 2 can view: person's institute delegate
            3: False, # person 3 cannot view
            4: True, # person 4 can view: self, is_staff
        })


    def test_admin_create_user_with_account(self):

        users = Person.objects.count()
        project = Project.objects.get(pid='TestProject1')
        p_users = project.users.count()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
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
        luser = ldap_schemas.account.objects.get(uid='samtest')
        self.assertEqual(luser.givenName, 'Sam')
        self.assertEqual(luser.homeDirectory, '/vpac/TestProject1/samtest')
        
     
    def test_admin_create_user(self):
        users = Person.objects.count()
        project = Project.objects.get(pid='TestProject1')
        project.users.count()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
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
        luser = ldap_schemas.person.objects.get(uid='samtest2')
        self.assertEqual(luser.givenName, 'Sam')
        # Try adding it again - Should fail
        response = self.client.post(reverse('kg_add_user'), form_data)
        self.failUnlessEqual(response.status_code, 200)


    def test_admin_update_user(self):
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.failUnlessEqual(logged_in, True)

        person = Person.objects.get(username='kgtestuser3')
        luser = ldap_schemas.account.objects.get(uid='kgtestuser3')
        self.failUnlessEqual(person.mobile, '')
        self.failUnlessEqual(luser.gidNumber, 500)
        self.failUnlessEqual(luser.o, 'Example')
        self.failUnlessEqual(luser.gecos, 'Test User3 (Example)')
        response = self.client.get(reverse('kg_user_edit', args=['kgtestuser3']))
        self.failUnlessEqual(response.status_code, 200)
        
        form_data = {
            'title' : 'Mr',
            'first_name': 'Test',
            'last_name': 'User3',
            'position': 'Sys Admin',
            'institute': 2,
            'department': 'eddf',
            'email': 'sam@vpac.org',
            'country': 'AU',
            'telephone': '4444444',
            'mobile': '555666',
        }
        response = self.client.post(reverse('kg_user_edit', args=['kgtestuser3']), form_data)
        self.failUnlessEqual(response.status_code, 302)

        person = Person.objects.get(username='kgtestuser3')
        luser = ldap_schemas.account.objects.get(uid='kgtestuser3')
        self.failUnlessEqual(person.mobile, '555666')
        self.failUnlessEqual(luser.gidNumber, 501)
        self.failUnlessEqual(luser.o, 'OtherInst')
        self.failUnlessEqual(luser.gecos, 'Test User3 (OtherInst)')

    def test_delete_activate_user(self):
        self.client.login(username='kgsuper', password='aq12ws')
        user = Person.objects.get(username='kgtestuser3')
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.project_set.count(), 1)
        self.assertEqual(user.useraccount_set.count(), 1)
        self.assertEqual(user.useraccount_set.all()[0].date_deleted, None)
        luser = ldap_schemas.person.objects.get(uid='kgtestuser3')
        self.assertEqual(luser.givenName, 'Test')

        response = self.client.get(reverse('admin_delete_user', args=[user.username]))
        self.failUnlessEqual(response.status_code, 200)
        # Test deleting
        response = self.client.post(reverse('admin_delete_user', args=[user.username]))
        self.failUnlessEqual(response.status_code, 302)
        
        user = Person.objects.get(username='kgtestuser3')

        self.assertEqual(user.is_active, False)
        self.assertEqual(user.project_set.count(), 0)
        self.assertEqual(user.useraccount_set.count(), 1)
        self.assertEqual(user.useraccount_set.all()[0].date_deleted, datetime.date.today())
        self.failUnlessRaises(ldap_schemas.person.DoesNotExist, ldap_schemas.person.objects.get, uid='kgtestuser3')

        # Test activating
        response = self.client.post(reverse('admin_activate_user', args=[user.username]))
        self.failUnlessEqual(response.status_code, 302)
        user = Person.objects.get(username='kgtestuser3')
        self.assertEqual(user.is_active, True)
        luser = ldap_schemas.person.objects.get(uid='kgtestuser3')
        self.assertEqual(luser.givenName, 'Test')


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
        user.useraccount_set.all()[0]

        self.assertEqual(user.project_set.count(), 1)

        Project.objects.create(
            pid='test2',
            name='test project 5',
            leader=Person.objects.get(username='leader'),
            start_date = datetime.date.today(),
            machine_category=MachineCategory.objects.get(name='VPAC'),
            institute=Institute.objects.get(name='VPAC'),
            is_active=True,
            is_approved=True,
        )

        response = self.client.post(reverse('kg_user_detail', args=[user.username]), { 'project': 'test2', 'project-add': 'true' })
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(user.project_set.count(), 2)
