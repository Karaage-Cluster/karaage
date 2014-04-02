# Copyright 2007-2014 VPAC
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
from django.conf import settings
from django.core.management import call_command

from captcha.models import CaptchaStore
from karaage.applications.models import Application, Applicant
from karaage.applications.models import ProjectApplication
from karaage.tests import fixtures


def set_admin():
    settings.ADMIN_IGNORED = False


def set_no_admin():
    settings.ADMIN_IGNORED = True


class UserApplicationTestCase(TestCase):

    def setUp(self):
        call_command('loaddata', 'karaage_data', **{'verbosity': 0})

    def tearDown(self):
        set_admin()

    def test_register_account(self):
        set_no_admin()

        self.assertEquals(len(mail.outbox), 0)
        response = self.client.get(reverse('kg_application_new'))
        self.failUnlessEqual(response.status_code, 200)
        a = response.content.find('name="captcha_0" type="hidden" value="')+38
        b = a+40
        hash_ = response.content[a:b]

        captcha_text = CaptchaStore.objects.get(hashkey=hash_).response

        # OPEN APPLICATION
        form_data = {
            'email': 'jim.bob@example.com',
            'captcha_0': hash_,
            'captcha_1': captcha_text,
        }

        response = self.client.post(
            reverse('kg_application_new'), form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver' + reverse('index'))
        token = Application.objects.get().secret_token
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue(
            mail.outbox[0].subject.startswith('TestOrg invitation'))
        self.assertEquals(mail.outbox[0].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[0].to[0], 'jim.bob@example.com')

        # SUBMIT APPLICANT DETAILS
        form_data = {
            'title': 'Mr',
            'short_name': 'Jim',
            'full_name': 'Jim Bob',
            'position': 'Researcher',
            'institute': 1,
            'department': 'Maths',
            'telephone': '4444444',
            'username': 'jimbob',
            'next': 'string',
        }

        response = self.client.post(
            reverse(
                'kg_application_unauthenticated',
                args=[token, 'O', 'applicant']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse(
                'kg_application_unauthenticated',
                args=[token, 'O', 'project']))

        # SUBMIT PROJECT DETAILS
        form_data = {
            'application_type': 'U',
            'project': 1,
            'aup': True,
            'make_leader': False,
            'additional_req': 'Meow',
            'needs_account': False,
            'submit': 'string',
            }

        response = self.client.post(
            reverse('kg_application_unauthenticated',
                    args=[token, 'O', 'project']),
            form_data, follow=True)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_unauthenticated', args=[token, 'L']))
        self.failUnlessEqual(response.status_code, 200)
        applicant = Applicant.objects.get(username='jimbob')
        application = applicant.applications.all()[0]
        self.failUnlessEqual(
            application.state,
            ProjectApplication.WAITING_FOR_LEADER)
        self.assertEquals(len(mail.outbox), 2)
        self.assertTrue(mail.outbox[1].subject.startswith('TestOrg request'))
        self.assertEquals(mail.outbox[1].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[1].to[0], 'leader@example.com')

        # LEADER LOGS IN TO APPROVE
        logged_in = self.client.login(
            username='kgtestuser1', password='aq12ws')
        self.failUnlessEqual(logged_in, True)

        # LEADER GET DETAILS
        response = self.client.get(
            reverse('kg_application_detail', args=[application.pk, 'L']))
        self.failUnlessEqual(response.status_code, 200)

        # LEADER GET DECLINE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'L', 'decline']))
        self.failUnlessEqual(response.status_code, 200)

        # LEADER GET APPROVE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'L', 'approve']))
        self.failUnlessEqual(response.status_code, 200)

        # LEADER APPROVE
        form_data = {
            'make_leader': False,
            'additional_req': 'Meow',
            'needs_account': False,
            }
        response = self.client.post(
            reverse('kg_application_detail',
                    args=[application.pk, 'L', 'approve']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_detail', args=[application.pk, 'K']))
        application = Application.objects.get(pk=application.id)
        self.failUnlessEqual(application.state, Application.WAITING_FOR_ADMIN)
        self.assertEquals(len(mail.outbox), 3)
        self.client.logout()

        # ADMIN LOGS IN TO APPROVE
        set_admin()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.failUnlessEqual(logged_in, True)

        # ADMIN GET DETAILS
        response = self.client.get(
            reverse('kg_application_detail', args=[application.pk, 'K']))
        self.failUnlessEqual(response.status_code, 200)

        # ADMIN GET DECLINE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'decline']))
        self.failUnlessEqual(response.status_code, 200)

        # ADMIN GET APPROVE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'approve']))
        self.failUnlessEqual(response.status_code, 200)

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
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_detail', args=[application.pk, 'P']))
        application = Application.objects.get(pk=application.id)
        self.failUnlessEqual(application.state, ProjectApplication.PASSWORD)
        self.assertEquals(len(mail.outbox), 4)
        self.client.logout()
        set_no_admin()

        # APPLICANT GET PASSWORD
        response = self.client.get(
            reverse('kg_application_unauthenticated', args=[token, 'P']))
        self.failUnlessEqual(response.status_code, 200)

        # APPLICANT SET PASSWORD
        form_data = {
            'new_password1': "Exaiquouxei0",
            'new_password2': "Exaiquouxei0",
            'submit': 'string',
            }

        response = self.client.post(
            reverse('kg_application_unauthenticated',
                    args=[token, 'P']), form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_unauthenticated', args=[token, 'C']))

        # APPLICANT GET COMPLETE
        response = self.client.get(
            reverse('kg_application_unauthenticated', args=[token, 'C']))
        self.failUnlessEqual(response.status_code, 200)

        # APPLICANT SET ARCHIVE
        form_data = {
            'archive': 'string',
            }
        response = self.client.post(
            reverse('kg_application_unauthenticated',
                    args=[token, 'C']),
            form_data, follow=False)
        # applicant not allowed to do this
        self.failUnlessEqual(response.status_code, 400)
        self.client.logout()

        # ADMIN ARCHIVE
        set_admin()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.failUnlessEqual(logged_in, True)
        response = self.client.post(
            reverse('kg_application_detail',
                    args=[application.pk, 'C']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_detail', args=[application.pk, 'A']))
        self.client.logout()
        set_no_admin()

        # APPLICANT GET ARCHIVE
        response = self.client.get(
            reverse('kg_application_unauthenticated', args=[token, 'A']))
        self.failUnlessEqual(response.status_code, 200)


class ProjectApplicationTestCase(TestCase):

    def setUp(self):
        call_command('loaddata', 'karaage_data', **{'verbosity': 0})

    def tearDown(self):
        set_admin()

    def test_register_account(self):
        set_no_admin()

        self.assertEquals(len(mail.outbox), 0)
        response = self.client.get(reverse('kg_application_new'))
        self.failUnlessEqual(response.status_code, 200)
        a = response.content.find('name="captcha_0" type="hidden" value="')+38
        b = a+40
        hash_ = response.content[a:b]

        captcha_text = CaptchaStore.objects.get(hashkey=hash_).response

        # OPEN APPLICATION
        form_data = {
            'email': 'jim.bob@example.com',
            'captcha_0': hash_,
            'captcha_1': captcha_text,
        }

        response = self.client.post(
            reverse('kg_application_new'), form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver' + reverse('index'))
        token = Application.objects.get().secret_token
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue(
            mail.outbox[0].subject.startswith('TestOrg invitation'))
        self.assertEquals(mail.outbox[0].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[0].to[0], 'jim.bob@example.com')

        # SUBMIT APPLICANT DETAILS
        form_data = {
            'title': 'Mr',
            'short_name': 'Jim',
            'full_name': 'Jim Bob',
            'position': 'Researcher',
            'institute': 1,
            'department': 'Maths',
            'telephone': '4444444',
            'username': 'jimbob',
            'next': 'string',
        }

        response = self.client.post(
            reverse('kg_application_unauthenticated',
                    args=[token, 'O', 'applicant']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_unauthenticated',
                      args=[token, 'O', 'project']))

        # SUBMIT PROJECT DETAILS
        form_data = {
            'application_type': 'P',
            'name': 'NewProject1',
            'description': "I like chocoloate.",
            'aup': True,
            'additional_req': 'Meow',
            'needs_account': False,
            'machine_categories': [1],
            'submit': 'string',
            }

        response = self.client.post(
            reverse('kg_application_unauthenticated',
                    args=[token, 'O', 'project']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_unauthenticated', args=[token, 'D']))
        applicant = Applicant.objects.get(username='jimbob')
        application = applicant.applications.all()[0]
        self.failUnlessEqual(
            application.state, ProjectApplication.WAITING_FOR_DELEGATE)
        self.assertEquals(len(mail.outbox), 2)
        self.assertTrue(mail.outbox[1].subject.startswith('TestOrg request'))
        self.assertEquals(mail.outbox[1].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[1].to[0], 'leader@example.com')

        # DELEGATE LOGS IN TO APPROVE
        logged_in = self.client.login(
            username='kgtestuser1', password='aq12ws')
        self.failUnlessEqual(logged_in, True)

        # DELEGATE GET DETAILS
        response = self.client.get(
            reverse('kg_application_detail', args=[application.pk, 'D']))
        self.failUnlessEqual(response.status_code, 200)

        # DELEGATE GET DECLINE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'D', 'decline']))
        self.failUnlessEqual(response.status_code, 200)

        # DELEGATE GET APPROVE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'D', 'approve']))
        self.failUnlessEqual(response.status_code, 200)

        # DELEGATE APPROVE
        form_data = {
            'additional_req': 'Meow',
            'needs_account': False,
            'machine_categories': [1],
            }
        response = self.client.post(
            reverse('kg_application_detail',
                    args=[application.pk, 'D', 'approve']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_detail', args=[application.pk, 'K']))
        application = Application.objects.get(pk=application.id)
        self.failUnlessEqual(application.state, Application.WAITING_FOR_ADMIN)
        self.assertEquals(len(mail.outbox), 3)
        self.client.logout()

        # ADMIN LOGS IN TO APPROVE
        set_admin()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.failUnlessEqual(logged_in, True)

        # ADMIN GET DETAILS
        response = self.client.get(
            reverse('kg_application_detail', args=[application.pk, 'K']))
        self.failUnlessEqual(response.status_code, 200)

        # ADMIN GET DECLINE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'decline']))
        self.failUnlessEqual(response.status_code, 200)

        # ADMIN GET APPROVE PAGE
        response = self.client.get(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'approve']))
        self.failUnlessEqual(response.status_code, 200)

        # ADMIN APPROVE
        form_data = {
            'additional_req': 'Woof',
            'needs_account': False,
            'machine_categories': [1],
            }
        response = self.client.post(
            reverse('kg_application_detail',
                    args=[application.pk, 'K', 'approve']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_detail', args=[application.pk, 'P']))
        application = Application.objects.get(pk=application.id)
        self.failUnlessEqual(application.state, ProjectApplication.PASSWORD)
        self.assertEquals(len(mail.outbox), 4)
        self.client.logout()
        set_no_admin()

        # APPLICANT GET PASSWORD
        response = self.client.get(
            reverse('kg_application_unauthenticated', args=[token, 'P']))
        self.failUnlessEqual(response.status_code, 200)

        # APPLICANT SET PASSWORD
        form_data = {
            'new_password1': "Exaiquouxei0",
            'new_password2': "Exaiquouxei0",
            'submit': 'string',
            }

        response = self.client.post(
            reverse('kg_application_unauthenticated', args=[token, 'P']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_unauthenticated', args=[token, 'C']))

        # APPLICANT GET COMPLETE
        response = self.client.get(
            reverse('kg_application_unauthenticated', args=[token, 'C']))
        self.failUnlessEqual(response.status_code, 200)

        # APPLICANT SET ARCHIVE
        form_data = {
            'archive': 'string',
            }
        response = self.client.post(
            reverse('kg_application_unauthenticated', args=[token, 'C']),
            form_data, follow=False)
        # applicant not allowed to do this
        self.failUnlessEqual(response.status_code, 400)
        self.client.logout()

        # ADMIN ARCHIVE
        set_admin()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.failUnlessEqual(logged_in, True)
        response = self.client.post(
            reverse('kg_application_detail', args=[application.pk, 'C']),
            form_data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(
            response.redirect_chain[0][0],
            'http://testserver'
            + reverse('kg_application_detail', args=[application.pk, 'A']))
        self.client.logout()
        set_no_admin()

        # APPLICANT GET ARCHIVE
        response = self.client.get(
            reverse('kg_application_unauthenticated', args=[token, 'A']))
        self.failUnlessEqual(response.status_code, 200)

    def _test_project_approval(self, application):
        admin = fixtures.PersonFactory(username='admin')
        admin.is_admin = True
        admin.save()
        application.approve(admin)

    def _test_project_make_leader(self, application):
        self._test_project_approval(application)
        if application.make_leader:
            self.assertIn(application.applicant,
                          application.project.leaders.all())
        else:
            self.assertNotIn(application.applicant,
                             application.project.leaders.all())

    def test_new_project_make_leader(self, make_leader=True):
        application = fixtures.ExistingProjectApplicationFactory()
        application.make_leader = make_leader
        self._test_project_make_leader(application)

    def test_new_project_make_leader_false(self):
        self.test_new_project_make_leader(make_leader=False)

    def test_existing_project_make_leader(self, make_leader=True):
        application = fixtures.NewProjectApplicationFactory()
        application.make_leader = make_leader
        self._test_project_make_leader(application)

    def test_existing_project_make_leader_false(self):
        self.test_existing_project_make_leader(make_leader=False)
