# Copyright 2010-2011, 2013-2015 VPAC
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

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.management import call_command

from karaage.middleware.threadlocals import reset
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.machines.models import Machine, MachineCategory


class AccountTestCase(TestCase):

    def setUp(self):
        def cleanup():
            reset()
        self.addCleanup(cleanup)

        call_command('loaddata', 'test_karaage', **{'verbosity': 0})
        form_data = {
            'title': 'Mr',
            'short_name': 'Sam',
            'full_name': 'Sam Morrison2',
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
        response = self.client.post(reverse('kg_person_add'), form_data)
        self.assertEqual(response.status_code, 302)

        person = Person.objects.get(username='kgsuper')
        self.assertEqual(person.short_name, 'Super')
        self.assertEqual(person.full_name, 'Super User')

    def test_add_account(self):
        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        response = self.client.get(
            reverse('kg_account_add', args=['samtest2']))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'username': person.username,
            'shell': '/bin/bash',
            'machine_category': 1,
            'default_project': 1,
        }

        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(username="samtest2")
        self.assertTrue(person.has_account(MachineCategory.objects.get(pk=1)))

    def test_fail_add_accounts_username(self):
        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        form_data = {
            'username': person.username,
            'shell': '/bin/bash',
            'machine_category': 1,
            'default_project': 1,
        }
        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertContains(
            response, "Username already in use on machine category Default")

    def test_fail_add_accounts_project(self):
        form_data = {
            'username': 'samtest2',
            'shell': '/bin/bash',
            'machine_category': 1,
            'default_project': 1,
        }
        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertContains(
            response, "Person does not belong to default project")

        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        form_data = {
            'username': person.username,
            'shell': '/bin/bash',
            'machine_category': 1,
            'default_project': 1,
        }
        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertEqual(response.status_code, 302)

        form_data = {
            'username': person.username,
            'shell': '/bin/bash',
            'machine_category': 2,
            'default_project': 1,
        }

        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertContains(
            response, "Default project not in machine category")

    def test_lock_unlock_account(self):
        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        response = self.client.get(reverse('kg_account_add',
                                           args=['samtest2']))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'username': person.username,
            'shell': '/bin/bash',
            'machine_category': 1,
            'default_project': 1,
        }

        response = self.client.post(
            reverse('kg_account_add', args=['samtest2']), form_data)
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(username='samtest2')
        ua = person.get_account(MachineCategory.objects.get(pk=1))
        self.assertEqual(person.is_locked(), False)
        self.assertEqual(ua.login_shell(), '/bin/bash')

        response = self.client.post(
            reverse('kg_person_lock', args=['samtest2']))
        person = Person.objects.get(username='samtest2')
        ua = person.get_account(MachineCategory.objects.get(pk=1))
        self.assertEqual(person.is_locked(), True)
        self.assertEqual(ua.login_shell(), '/bin/bash')

        response = self.client.post(
            reverse('kg_person_unlock', args=['samtest2']))
        person = Person.objects.get(username='samtest2')
        ua = person.get_account(MachineCategory.objects.get(pk=1))
        self.assertEqual(person.is_locked(), False)
        self.assertEqual(ua.login_shell(), '/bin/bash')


class MachineTestCase(TestCase):

    def setUp(self):
        today = datetime.datetime.now()
        # 10cpus
        mach1 = Machine.objects.get(pk=1)
        mach1.start_date = today - datetime.timedelta(days=80)
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

    def do_availablity_test(self, start, end, mc, expected_time, expected_cpu):
        from karaage.cache.usage import get_machine_category_usage
        cache = get_machine_category_usage(mc, start.date(), end.date())
        available_time = cache.available_time
        self.assertEqual(available_time, expected_time)

    def no_test_available_time(self):
        mc1 = MachineCategory.objects.get(pk=1)
        MachineCategory.objects.get(pk=2)
        for machine in Machine.objects.all():
            machine.category = mc1
            machine.save()

        day = 60 * 60 * 24
        today = datetime.datetime.now()

        end = today - datetime.timedelta(days=20)
        start = today - datetime.timedelta(days=30)
        self.do_availablity_test(start, end, mc1, 8050 * day * 11, 8050)

        start = today - datetime.timedelta(days=99)
        end = today - datetime.timedelta(days=90)
        self.do_availablity_test(start, end, mc1, 40 * day * 10, 40)

        start = today - datetime.timedelta(days=85)
        end = today - datetime.timedelta(days=76)
        self.do_availablity_test(start, end, mc1, 45 * day * 10, 45)

        start = today - datetime.timedelta(days=35)
        end = today - datetime.timedelta(days=16)
        self.do_availablity_test(start, end, mc1, 6042 * day * 20, 6042)

        start = today - datetime.timedelta(days=20)
        end = today - datetime.timedelta(days=20)
        self.do_availablity_test(start, end, mc1, 8050 * day, 8050)
