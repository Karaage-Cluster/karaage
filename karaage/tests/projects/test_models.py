# Copyright 2014-2015 VPAC
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

from django.core import exceptions as django_exceptions
import mock
import unittest

from karaage.tests.unit import UnitTestCase
from karaage.projects.models import Project, ProjectQuota
from karaage.tests.fixtures import (ProjectFactory, InstituteFactory,
                                    GroupFactory, simple_account)


class ProjectTestCase(UnitTestCase):

    def test_minimum_create(self):
        institute = InstituteFactory()
        project = Project.objects.create(
            pid='test',
            name='Test',
            institute=institute)

        project.full_clean()
        self.assertEqual(project.name, 'Test')
        self.assertEqual(project.pid, 'test')
        self.assertEqual(project.institute, institute)
        self.assertEqual(project.group.name, 'test')
        self.assertFalse(project.is_approved)
        self.assertEqual(project.leaders.count(), 0)
        self.assertTrue(project.description is None)
        self.assertTrue(project.deleted_by is None)
        self.assertTrue(project.date_deleted is None)
        self.assertTrue(project.approved_by is None)
        self.assertTrue(project.date_approved is None)
        self.assertTrue(project.last_usage is None)
        self.assertTrue(project.additional_req is None)

    @unittest.skip("broken with mysql/postgresql")
    def test_pid(self):
        assert_raises = self.assertRaises(django_exceptions.ValidationError)

        # Max length
        person = ProjectFactory(pid="a" * 255)
        person.full_clean()

        # Name is too long
        person = ProjectFactory(pid="a" * 256)
        with assert_raises:
            person.full_clean()

    def test_change_group(self):
        """Check that when changing an projects group, old accounts are
        removed from the project and new ones are added.

        """
        account1 = simple_account(machine_category=self.machine_category)
        group1 = GroupFactory()
        group1.add_person(account1.person)
        institute = InstituteFactory()

        # Test during initial creation of the project
        self.resetDatastore()
        project = Project.objects.create(group=group1, institute=institute)
        project_quota = ProjectQuota.objects.create(
            machine_category=self.machine_category, project=project)
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_project(project),
             mock.call.add_account_to_project(account1, project)])

        # Test changing an existing projects group
        account2 = simple_account(machine_category=self.machine_category)
        self.resetDatastore()
        group2 = GroupFactory()
        group2.add_person(account2.person)
        project.group = group2
        project.save()
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.save_group(group2),
             mock.call.add_account_to_group(account2, group2),
             mock.call.save_project(project),
             # old accounts are removed
             mock.call.remove_account_from_project(account1, project),
             # new accounts are added
             mock.call.add_account_to_project(account2, project)])

        # Test deleting project quota
        self.resetDatastore()
        project_quota.delete()
        self.assertEqual(
            self.datastore.method_calls,
            [mock.call.remove_account_from_project(account2, project),
             mock.call.delete_project(project)])
