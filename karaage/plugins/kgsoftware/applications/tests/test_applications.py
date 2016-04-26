# Copyright 2015 VPAC
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

import django
from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.management import call_command

from karaage.people.models import Group

from karaage.plugins.kgapplications.models import Application

from ...models import Software, SoftwareLicense
from ..models import SoftwareApplication


def set_admin():
    settings.ADMIN_IGNORED = False


def set_no_admin():
    settings.ADMIN_IGNORED = True


class SoftwareApplicationTestCase(TestCase):

    def setUp(self):
        call_command('loaddata', 'test_karaage', **{'verbosity': 0})

    def tearDown(self):
        set_admin()

    def test_register_software(self):
        if django.VERSION >= (1, 9):
            url_prefix = ""
        else:
            url_prefix = 'http://testserver'

        group = Group.objects.create(name="windows")
        software = Software.objects.create(
            name="windows",
            restricted=True,
            group=group,
        )
        SoftwareLicense.objects.create(
            software=software,
            version="3.11",
            text="You give your soal to the author "
            "if you wish to access this software.",
        )

        set_no_admin()

        # APPLICANT LOGS IN
        logged_in = self.client.login(
            username='kgtestuser1', password='aq12ws')
        self.assertEqual(logged_in, True)
        self.assertEqual(len(mail.outbox), 0)

        response = self.client.get(
            reverse('kg_software_detail', args=[software.pk]))
        self.assertEqual(response.status_code, 200)

        # OPEN APPLICATION
        form_data = {
        }

        response = self.client.post(
            reverse('kg_software_detail', args=[software.pk]),
            form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        application = Application.objects.get()
        self.assertEqual(
            response.redirect_chain[0][0],
            url_prefix +
            reverse('kg_application_detail', args=[application.pk, 'O']))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'TestOrg invitation: access software windows')
        self.assertEqual(mail.outbox[0].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEqual(mail.outbox[0].to[0], 'leader@example.com')

        # SUBMIT APPLICATION
        form_data = {
            'submit': True,
        }

        response = self.client.post(
            reverse('kg_application_detail', args=[application.pk, 'O']),
            form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0],
            url_prefix +
            reverse('kg_application_detail', args=[application.pk, 'K']))

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[1].subject, 'TestOrg request: access software windows')
        self.assertEqual(mail.outbox[1].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEqual(mail.outbox[1].to[0], 'sam@vpac.org')

        # ADMIN LOGS IN TO APPROVE
        set_admin()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.assertEqual(logged_in, True)

        # ADMIN GET DETAILS
        response = self.client.get(
            reverse('kg_application_detail', args=[application.pk, 'K']))
        self.assertEqual(response.status_code, 200)

        # ADMIN GET DECLINE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'decline']))
        self.assertEqual(response.status_code, 200)

        # ADMIN GET APPROVE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'approve']))
        self.assertEqual(response.status_code, 200)

        # ADMIN APPROVE
        form_data = {
            'make_leader': False,
            'additional_req': 'Woof',
            'needs_account': False,
        }
        response = self.client.post(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'approve']),
            form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0],
            url_prefix +
            reverse('kg_application_detail', args=[application.pk, 'C']))
        application = Application.objects.get(pk=application.id)
        self.assertEqual(application.state, SoftwareApplication.COMPLETED)
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(
            mail.outbox[2].subject,
            'TestOrg approved: access software windows')
        self.assertEqual(mail.outbox[2].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEqual(mail.outbox[2].to[0], 'leader@example.com')
        self.client.logout()
        set_no_admin()

        # test group
        groups = Group.objects.filter(
            name="windows", members__username="kgtestuser1")
        self.assertEqual(len(groups), 1)
