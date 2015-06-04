# Copyright 2009-2010, 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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

import datetime

from django.core.urlresolvers import reverse
from django.core.management import call_command

from karaage.people.models import Person, Group
from karaage.projects.models import Project
from karaage.machines.models import Account
from karaage.tests.integration import IntegrationTestCase


class ProjectTestCase(IntegrationTestCase):

    def setUp(self):
        super(ProjectTestCase, self).setUp()
        call_command('loaddata', 'test_karaage', **{'verbosity': 0})
        self._datastore = self.mc_ldap_datastore

    def test_admin_add_project(self):

        Project.objects.count()

        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_project_add'))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 4',
            'description': 'Test',
            'institute': 1,
            'leaders': "|2|3|",
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_project_add'), form_data)
        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(name='Test Project 4')

        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(
            project.approved_by,
            Person.objects.get(username='kgsuper'))
        self.assertEqual(project.pid, 'pExam0001')
        self.assertTrue(Person.objects.get(pk=2) in project.leaders.all())
        self.assertTrue(Person.objects.get(pk=3) in project.leaders.all())
        lgroup = self._datastore._groups().get(cn=project.pid)
        self.assertEqual(lgroup.cn, project.pid)

    def test_admin_add_project_pid(self):
        Project.objects.count()

        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(reverse('kg_project_add'))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'pid': "Enrico",
            'name': 'Test Project 4',
            'description': 'Test',
            'institute': 1,
            'leaders': "|2|3|",
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_project_add'), form_data)
        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(pid="Enrico")

        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(
            project.approved_by,
            Person.objects.get(username='kgsuper'))
        self.assertEqual(project.pid, 'Enrico')
        self.assertTrue(Person.objects.get(pk=2) in project.leaders.all())
        self.assertTrue(Person.objects.get(pk=3) in project.leaders.all())
        lgroup = self._datastore._groups().get(cn=project.pid)
        self.assertEqual(lgroup.cn, project.pid)

    def test_add_remove_user_to_project(self):
        self.assertRaises(
            self._datastore._account.DoesNotExist,
            self._datastore._accounts().get, pk='kgtestuser2')

        # login
        self.client.login(username='kgsuper', password='aq12ws')

        # get project details
        project = Project.objects.get(pid='TestProject1')
        self.assertEqual(project.group.members.count(), 1)
        response = self.client.get(
            reverse('kg_project_detail', args=[project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertRaises(
            self._datastore._account.DoesNotExist,
            self._datastore._accounts().get, pk='kgtestuser2')

        # add kgtestuser2 to project
        new_user = Person.objects.get(username='kgtestuser2')
        response = self.client.post(
            reverse('kg_project_detail', args=[project.id]),
            {'person': new_user.id})
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(pid='TestProject1')
        self.assertEqual(project.group.members.count(), 2)
        lgroup = self._datastore._groups().get(cn=project.pid)
        self._datastore._accounts().get(pk='kgtestuser2')
        lgroup.secondary_accounts.get(pk='kgtestuser2')

        # remove user
        for account in new_user.account_set.all():
            account.default_project = None
            account.save()
        response = self.client.post(
            reverse('kg_remove_project_member',
                    args=[project.id, new_user.username]))
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(pid='TestProject1')
        self.assertEqual(project.group.members.count(), 1)
        lgroup = self._datastore._groups().get(cn=project.pid)
        self.assertRaises(
            self._datastore._account.DoesNotExist,
            lgroup.secondary_accounts.get,
            pk='kgtestuser2')

    def test_delete_project(self):

        self.client.login(username='kgsuper', password='aq12ws')

        project = Project.objects.get(pid='TestProject1')
        for account in Account.objects.filter(default_project=project):
            account.default_project = None
            account.save()

        self.assertEqual(project.is_active, True)

        response = self.client.post(
            reverse('kg_project_delete', args=[project.id]))
        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(pid='TestProject1')

        self.assertEqual(project.is_active, False)
        self.assertEqual(project.group.members.count(), 0)
        self.assertEqual(project.date_deleted, datetime.date.today())
        self.assertEqual(
            project.deleted_by,
            Person.objects.get(username='kgsuper'))

    def test_change_default(self):
        pass

    def test_admin_edit_project(self):
        project = Project.objects.get(pid='TestProject1')
        self.assertEqual(project.is_active, True)
        self.assertEqual(project.name, 'Test Project 1')
        self.assertTrue(Person.objects.get(pk=1) in project.leaders.all())
        self.assertFalse(Person.objects.get(pk=2) in project.leaders.all())
        self.assertFalse(Person.objects.get(pk=3) in project.leaders.all())
        self.assertTrue(
            Person.objects.get(pk=3) in project.group.members.all())

        self.client.login(username='kgsuper', password='aq12ws')
        response = self.client.get(
            reverse('kg_project_edit', args=[project.id]))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 1 was 4',
            'description': 'Test',
            'institute': 1,
            'leaders': "|2|3|",
            'start_date': project.start_date,
        }

        response = self.client.post(
            reverse('kg_project_edit', args=[project.id]),
            form_data)
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(pid='TestProject1')
        self.assertEqual(project.is_active, True)
        # this is not changed because we don't support editing leaders with
        # this interface any more
        self.assertTrue(Person.objects.get(pk=1) in project.leaders.all())
        self.assertFalse(Person.objects.get(pk=2) in project.leaders.all())
        self.assertFalse(Person.objects.get(pk=3) in project.leaders.all())
        lgroup = self._datastore._groups().get(cn=project.pid)
        self.assertEqual(lgroup.cn, project.pid)

    def test_user_add_project(self):
        pass

    def test_user_edit_project(self):
        pass

    def test_change_group(self):
        group, _ = Group.objects.get_or_create(name='example')
        project = Project.objects.get(pid='TestProject1')
        project.group = group
        project.save()
