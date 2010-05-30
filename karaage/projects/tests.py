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
from django.core import mail
from django.core.urlresolvers import reverse

from placard.server import slapd
import datetime

from karaage.people.models import Person
from karaage.test_data.initial_ldap_data import test_ldif
from karaage.projects.models import Project


class ProjectTestCase(TestCase):

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

    def test_admin_add_project(self):
        projects = Project.objects.count()
        
        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 4',
            'institute': 1,
            'leader': 2,
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

    def test_admin_add_project_pid(self):
        projects = Project.objects.count()
        
        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'pid': "Enrico",
            'name': 'Test Project 4',
            'institute': 1,
            'leader': 2,
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


    def test_add_remove_user_to_project(self):
        self.client.login(username='kgsuper', password='aq12ws')
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.users.count(), 1)
        response = self.client.get(reverse('kg_project_detail', args=[project.pid]))
        self.failUnlessEqual(response.status_code, 200)
        
        new_user = Person.objects.get(user__username='kgtestuser2')
        response = self.client.post(reverse('kg_project_detail', args=[project.pid]), { 'person': new_user.id} )
        self.failUnlessEqual(response.status_code, 200)
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.users.count(), 2)
        
        # remove user
        response = self.client.post(reverse('kg_remove_project_member', args=[project.pid, new_user.username]))
        self.failUnlessEqual(response.status_code, 302)
        project = Project.objects.get(pk='TestProject1')
        self.assertEqual(project.users.count(), 1)
        
        
    def test_delete_project(self):

        self.client.login(username='kgsuper', password='aq12ws')

        project = Project.objects.get(pk='TestProject1')

        self.assertEqual(project.is_active, True)
        
        response = self.client.post(reverse('kg_delete_project', args=[project.pid]))
        self.failUnlessEqual(response.status_code, 302)
        
        project = Project.objects.get(pk='TestProject1')

        self.assertEqual(project.is_active, False)
        self.assertEqual(project.users.count(), 0)
        self.assertEqual(project.date_deleted, datetime.date.today())
        self.assertEqual(project.deleted_by, Person.objects.get(user__username='kgsuper'))
        
