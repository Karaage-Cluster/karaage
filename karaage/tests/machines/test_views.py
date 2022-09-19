# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import pytest
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from karaage.machines.models import Machine
from karaage.middleware.threadlocals import reset
from karaage.people.models import Person
from karaage.projects.models import Project


@pytest.mark.django_db
class AccountTestCase(TestCase):
    def setUp(self):
        def cleanup():
            reset()

        self.addCleanup(cleanup)

        call_command("loaddata", "test_karaage", **{"verbosity": 0})
        form_data = {
            "title": "Mr",
            "short_name": "Sam",
            "full_name": "Sam Morrison2",
            "position": "Sys Admin",
            "institute": 1,
            "department": "eddf",
            "email": "sam2@vpac.org",
            "country": "AU",
            "telephone": "4444444",
            "username": "samtest2",
            "password1": "Exaiquouxei0",
            "password2": "Exaiquouxei0",
            "needs_account": False,
        }
        self.client.login(username="kgsuper", password="aq12ws")
        response = self.client.post(reverse("kg_person_add"), form_data)
        self.assertEqual(response.status_code, 302)

        person = Person.objects.get(username="kgsuper")
        self.assertEqual(person.short_name, "Super")
        self.assertEqual(person.full_name, "Super User")

    def test_add_account(self):
        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        response = self.client.get(reverse("kg_account_add", args=["samtest2"]))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "username": person.username,
            "shell": "/bin/bash",
            "default_project": 1,
        }

        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(username="samtest2")
        self.assertTrue(person.has_account())

    def test_fail_add_accounts_username(self):
        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        form_data = {
            "username": person.username,
            "shell": "/bin/bash",
            "default_project": 1,
        }
        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertContains(response, "Username already in use.")

    def test_fail_add_accounts_project(self):
        form_data = {
            "username": "samtest2",
            "shell": "/bin/bash",
            "default_project": 1,
        }
        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertContains(response, "Person does not belong to default project")

        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        form_data = {
            "username": person.username,
            "shell": "/bin/bash",
            "default_project": 1,
        }
        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertEqual(response.status_code, 302)

        form_data = {
            "username": person.username,
            "shell": "/bin/bash",
            "default_project": 1,
        }

        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertContains(response, "Username already in use.")

    def test_lock_unlock_account(self):
        project = Project.objects.get(pk=1)
        person = Person.objects.get(username="samtest2")
        person.groups.add(project.group)

        response = self.client.get(reverse("kg_account_add", args=["samtest2"]))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "username": person.username,
            "shell": "/bin/bash",
            "default_project": 1,
        }

        response = self.client.post(reverse("kg_account_add", args=["samtest2"]), form_data)
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(username="samtest2")
        ua = person.get_account()
        self.assertEqual(person.is_locked(), False)
        self.assertEqual(ua.login_shell(), "/bin/bash")

        response = self.client.post(reverse("kg_person_lock", args=["samtest2"]))
        person = Person.objects.get(username="samtest2")
        ua = person.get_account()
        self.assertEqual(person.is_locked(), True)
        self.assertEqual(ua.login_shell(), "/bin/bash")

        response = self.client.post(reverse("kg_person_unlock", args=["samtest2"]))
        person = Person.objects.get(username="samtest2")
        ua = person.get_account()
        self.assertEqual(person.is_locked(), False)
        self.assertEqual(ua.login_shell(), "/bin/bash")


@pytest.mark.django_db
class MachineTestCase(TestCase):
    def setUp(self):
        today = timezone.now()
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
