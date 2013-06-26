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
from django.core.management import call_command

from tldap.test import slapd
import datetime

from karaage.people.models import Person
from karaage.test_data.initial_ldap_data import test_ldif
from karaage.projects.models import Project
from karaage.datastores import ldap_schemas


class ProjectTestCase(TestCase):

    def setUp(self):
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        call_command('loaddata', 'karaage/testproject/karaage_data', **{'verbosity': 0})
        self.server = server

    def tearDown(self):
        self.server.stop()

    def test_admin_add_project(self):

        Project.objects.count()
        
        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 4',
            'description': 'Test',
            'institute': 1,
            'leaders': [2,3],
            'machine_category': 1,
            'machine_categories': [1,],
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_add_project'), form_data)
        self.failUnlessEqual(response.status_code, 302)
        
        project = Project.objects.get(name='Test Project 4')
        
        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(project.approved_by, Person.objects.get(user__username='kgsuper'))
        self.assertEqual(project.pid, 'pExam0001')
        self.assertTrue(Person.objects.get(pk=2) in project.leaders.all())
        self.assertTrue(Person.objects.get(pk=3) in project.leaders.all())    
        lgroup = ldap_schemas.group.objects.get(cn=project.pid)
        self.assertEqual(lgroup.cn, project.pid)

    def test_admin_add_project_pid(self):
        Project.objects.count()
        
        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'pid': "Enrico",
            'name': 'Test Project 4',
            'description': 'Test',
            'institute': 1,
            'leaders': [2,3],
            'machine_category': 1,
            'machine_categories': [1,],
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_add_project'), form_data)
        self.failUnlessEqual(response.status_code, 302)
        
        project = Project.objects.get(pid="Enrico")
        
        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(project.approved_by, Person.objects.get(user__username='kgsuper'))
        self.assertEqual(project.pid, 'Enrico')
        self.assertTrue(Person.objects.get(pk=2) in project.leaders.all())
        self.assertTrue(Person.objects.get(pk=3) in project.leaders.all())
        lgroup = ldap_schemas.group.objects.get(cn=project.pid)
        self.assertEqual(lgroup.cn, project.pid)

    def test_add_remove_user_to_project(self):
        self.assertRaises(ldap_schemas.person.DoesNotExist, ldap_schemas.person.objects.get, pk='kgtestuser2')

        # login
        self.client.login(username='kgsuper', password='aq12ws')

        # get project details
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.group.members.count(), 1)
        response = self.client.get(reverse('kg_project_detail', args=[project.pid]))
        self.failUnlessEqual(response.status_code, 200)
        self.assertRaises(ldap_schemas.person.DoesNotExist, ldap_schemas.person.objects.get, pk='kgtestuser2')

        # add kgtestuser2 to project
        new_user = Person.objects.get(user__username='kgtestuser2')
        response = self.client.post(reverse('kg_project_detail', args=[project.pid]), { 'person': new_user.id} )
        self.failUnlessEqual(response.status_code, 302)
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.group.members.count(), 2)
        lgroup = ldap_schemas.group.objects.get(cn=project.pid)
        ldap_schemas.person.objects.get(pk='kgtestuser2')
        lgroup.secondary_persons.get(pk='kgtestuser2')

        # remove user
        response = self.client.post(reverse('kg_remove_project_member', args=[project.pid, new_user.username]))
        self.failUnlessEqual(response.status_code, 302)
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.group.members.count(), 1)
        lgroup = ldap_schemas.group.objects.get(cn=project.pid)
        self.assertRaises(ldap_schemas.person.DoesNotExist, lgroup.secondary_persons.get, pk='kgtestuser2')

    def test_delete_project(self):

        self.client.login(username='kgsuper', password='aq12ws')

        project = Project.objects.get(pk='TestProject1')

        self.assertEqual(project.is_active, True)
        
        response = self.client.post(reverse('kg_delete_project', args=[project.pid]))
        self.failUnlessEqual(response.status_code, 302)
        
        project = Project.objects.get(pk='TestProject1')

        self.assertEqual(project.is_active, False)
        self.assertEqual(project.group.members.count(), 0)
        self.assertEqual(project.date_deleted, datetime.date.today())
        self.assertEqual(project.deleted_by, Person.objects.get(user__username='kgsuper'))
        

    def test_change_deafult(self):
        pass

    def test_admin_edit_project(self):
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.is_active, True)
        self.assertEqual(project.name, 'Test Project 1')
        self.assertTrue(Person.objects.get(pk=1) in project.leaders.all())
        self.assertTrue(Person.objects.get(pk=3) in project.group.members.all())

        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_edit_project', args=['TestProject1']))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 1 was 4',
            'description': 'Test',
            'institute': 1,
            'leaders': [2,3],
            'machine_category': 1,
            'machine_categories': [1,],
            'start_date': project.start_date,
        }

        response = self.client.post(reverse('kg_edit_project', args=['TestProject1']), form_data)
        self.failUnlessEqual(response.status_code, 302)   
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.is_active, True)
        self.assertTrue(Person.objects.get(pk=2) in project.leaders.all())
        self.assertTrue(Person.objects.get(pk=3) in project.leaders.all())    
        lgroup = ldap_schemas.group.objects.get(cn=project.pid)
        self.assertEqual(lgroup.cn, project.pid)


    def test_user_add_project(self):
        pass

    def test_user_edit_project(self):
        pass

