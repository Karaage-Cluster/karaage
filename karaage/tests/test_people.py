# Copyright 2009-2010, 2013-2015 VPAC
# Copyright 2010-2011, 2014 The University of Melbourne
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
import re

import django
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core import mail
from django.contrib import auth

from karaage.people.models import Person
from karaage.institutes.models import Institute, InstituteDelegate
from karaage.projects.models import Project
from karaage.machines.models import Account, MachineCategory
from karaage.tests.integration import IntegrationTestCase


class FakeRequest(object):

    def __init__(self, person):
        self.user = person


class PersonTestCase(IntegrationTestCase):
    fixtures = [
        'test_karaage.json',
    ]

    def setUp(self):
        super(PersonTestCase, self).setUp()
        self._datastore = self.mc_ldap_datastore

    def test_login(self):
        if django.VERSION >= (1, 9):
            url_prefix = ""
        else:
            url_prefix = 'http://testserver'

        form_data = {
            'username': 'kgsuper',
            'password': 'aq12ws',
        }

        response = self.client.post(
            reverse('kg_profile_login'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0],
            url_prefix + reverse('index'))

        user = auth.get_user(self.client)
        assert user.is_authenticated()
        assert user.username == 'kgsuper'

    def test_saml_login(self):
        person = Person.objects.get(username='kgtestuser1')
        person.institute = Institute.objects.get(pk=3)
        person.saml_id = "pY9RL3RHeQwAm4Hd"
        person.save()

        form_data = {
            'login': 'true',
            'institute': 3,
        }

        response = self.client.post(
            reverse('kg_profile_login_saml'), form_data, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.redirect_chain[0][0],
            "https://testserver/Shibboleth.sso/Login" +
            "?target=https://testserver/&entityID=http://samlid")

        response = self.client.get(
            reverse('index'),
            HTTP_SHIB_SESSION_ID="yes",
            HTTP_SHIB_IDENTITY_PROVIDER="http://samlid",
            HTTP_PERSISTENT_ID="pY9RL3RHeQwAm4Hd",
            HTTP_MAIL="email@example.org",
            HTTP_GIVENNAME="Firstname",
            HTTP_SN="Surname",
            HTTP_TELEPHONENUMBER="000",
            HTTP_UID="somethingelse"
        )
        self.assertEqual(response.status_code, 200)

        user = auth.get_user(self.client)
        assert user.is_authenticated()
        assert user.username == 'kgtestuser1'

    def test_logout(self):
        if django.VERSION >= (1, 9):
            url_prefix = ""
        else:
            url_prefix = 'http://testserver'

        response = self.client.post(reverse('kg_profile_logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[0][0],
            url_prefix + reverse('index'))

        user = auth.get_user(self.client)
        assert not user.is_authenticated()

    def do_permission_tests(self, test_object, users):
        for user_id in users:
            # print("can user '%d' access '%s'?"%(user_id, test_object))
            person = Person.objects.get(id=user_id)
            request = FakeRequest(person)
            result = test_object.can_view(request)
            expected_result = users[user_id]
            # print("---> got:'%s' expected:'%s'"%(result, expected_result))
            self.assertEqual(
                result, expected_result,
                "%r.can_view(%r) returned %r but we expected %r"
                % (test_object, person, result, expected_result))
            # print()

    def test_permissions(self):
        test_object = Project.objects.get(pid="TestProject1")
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate,
                        #                    project leader
            2: False,   # person 2 cannot view
            3: True,    # person 3 can view: project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=1)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: self, project member,
                        #                    person's institute delegate
            2: False,   # person 2 cannot view
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: is_staff, institute delegate
        })

        test_object = Person.objects.get(id=2)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate
            2: True,    # person 2 can view: self
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=3)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate,
                        # project leader
            2: False,   # person 2 cannot view
            3: True,    # person 3 can view: self, project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=4)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate
            2: False,   # person 2 cannot view
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: self, is_staff
        })

        # add user 2 to project
        # test that members can see other people in own project
        # print("------------------------------------------------------------")
        project = Project.objects.get(pid="TestProject1")
        project.group.members = [2, 3]

        test_object = Project.objects.get(pid="TestProject1")
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate
            2: True,    # person 2 can view: project member
            3: True,    # person 3 can view: project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=1)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: self, project member,
                        #                    delegate of institute
            2: False,   # person 2 cannot view
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=2)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate,
                        #                    project leader
            2: True,    # person 2 can view: self
            3: True,    # person 3 can view: project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=3)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate,
                        #                    project leader
            2: True,    # person 2 can view: project member
            3: True,    # person 3 can view: self, project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=4)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate
            2: False,   # person 2 cannot view
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: self, is_staff
        })

        # change institute of all people
        # Test institute leader can access people in project despite not being
        # institute leader for these people.
        # print("------------------------------------------------------------")
        Person.objects.all().update(institute=2)
        # Institute.objects.filter(pk=2).update(delegate=2,active_delegate=2)
        InstituteDelegate.objects.get_or_create(
            institute=Institute.objects.get(id=2),
            person=Person.objects.get(id=2),
            defaults={'send_email': False})
        project = Project.objects.get(pid="TestProject1")
        project.leaders = [2]

        test_object = Project.objects.get(pid="TestProject1")
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate
            2: True,    # person 2 can view: project member, person's
                        #                    institute delegate, project leader
            3: True,    # person 3 can view: project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=1)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: self, project member
            2: True,    # person 2 can view: person's institute delegate
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=2)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: project's institute leader
            2: True,    # person 2 can view: self, person's institute delegate,
                        #                    project leader
            3: True,    # person 3 can view: project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=3)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: project's institute leader
            2: True,    # person 2 can view: project member, person's institute
                        #                    delegate, project leader
            3: True,    # person 3 can view: self, project member
            4: True,    # person 4 can view: is_staff
        })

        test_object = Person.objects.get(id=4)
        self.do_permission_tests(test_object, {
            1: True,    # person 1 can view: person's institute delegate
            2: True,    # person 2 can view: person's institute delegate
            3: False,   # person 3 cannot view
            4: True,    # person 4 can view: self, is_staff
        })

    def test_admin_create_user_with_account(self):
        users = Person.objects.count()
        project = Project.objects.get(pid='TestProject1')
        p_users = project.group.members.count()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.assertEqual(logged_in, True)
        response = self.client.get(reverse('kg_person_add'))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'title': 'Mr',
            'short_name': 'Sam',
            'full_name': 'Sam Morrison',
            'position': 'Sys Admin',
            'institute': 1,
            'department': 'eddf',
            'email': 'sam@vpac.org',
            'country': 'AU',
            'telephone': '4444444',
            'username': 'samtest',
            'password1': 'Exaiquouxei0',
            'password2': 'Exaiquouxei0',
            'project': 1,
            'needs_account': True,
            'machine_category': 1,
        }

        response = self.client.post(reverse('kg_person_add'), form_data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Person.objects.count(), users + 1)
        users = users + 1
        person = Person.objects.get(username='samtest')
        self.assertEqual(person.is_active, True)
        self.assertEqual(person.username, 'samtest')
        self.assertEqual(Account.objects.count(), 2)
        self.assertEqual(project.group.members.count(), p_users + 1)
        luser = self._datastore._accounts().get(uid='samtest')
        self.assertEqual(luser.givenName, 'Sam')
        self.assertEqual(luser.homeDirectory, '/vpac/TestProject1/samtest')

    def test_admin_create_user(self):
        users = Person.objects.count()
        project = Project.objects.get(pid='TestProject1')
        project.group.members.count()
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.assertEqual(logged_in, True)
        response = self.client.get(reverse('kg_person_add'))

        self.assertEqual(response.status_code, 200)

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

        response = self.client.post(reverse('kg_person_add'), form_data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Person.objects.count(), users + 1)
        users = users + 1
        person = Person.objects.get(username='samtest2')
        self.assertEqual(person.is_active, True)
        self.assertEqual(person.username, 'samtest2')
        # Try adding it again - Should fail
        response = self.client.post(reverse('kg_person_add'), form_data)
        self.assertEqual(response.status_code, 200)

    def test_admin_update_person(self):
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.assertEqual(logged_in, True)

        person = Person.objects.get(username='kgtestuser3')
        luser = self._datastore._accounts().get(uid='kgtestuser3')
        self.assertEqual(person.mobile, '')
        self.assertEqual(luser.gidNumber, 500)
        self.assertEqual(luser.o, 'Example')
        self.assertEqual(luser.gecos, 'Test User3 (Example)')
        response = self.client.get(
            reverse('kg_person_edit', args=['kgtestuser3']))
        self.assertEqual(response.status_code, 200)

        form_data = {
            'title': 'Mr',
            'short_name': 'Test',
            'full_name': 'Test User3',
            'position': 'Sys Admin',
            'institute': 2,
            'department': 'eddf',
            'email': 'sam@vpac.org',
            'country': 'AU',
            'telephone': '4444444',
            'mobile': '555666',
        }
        response = self.client.post(
            reverse('kg_person_edit', args=['kgtestuser3']), form_data)
        self.assertEqual(response.status_code, 302)

        person = Person.objects.get(username='kgtestuser3')
        luser = self._datastore._accounts().get(uid='kgtestuser3')
        self.assertEqual(person.mobile, '555666')
        self.assertEqual(luser.gidNumber, 501)
        self.assertEqual(luser.o, 'OtherInst')
        self.assertEqual(luser.gecos, 'Test User3 (OtherInst)')

    def test_delete_activate_person(self):
        self.client.login(username='kgsuper', password='aq12ws')
        person = Person.objects.get(username='kgtestuser3')
        self.assertEqual(person.is_active, True)
        self.assertEqual(person.projects.count(), 1)
        self.assertEqual(person.account_set.count(), 1)
        self.assertEqual(person.account_set.all()[0].date_deleted, None)
        luser = self._datastore._accounts().get(uid='kgtestuser3')
        self.assertEqual(luser.givenName, 'Test')

        response = self.client.get(
            reverse('kg_person_delete', args=[person.username]))
        self.assertEqual(response.status_code, 200)
        # Test deleting
        response = self.client.post(
            reverse('kg_person_delete', args=[person.username]))
        self.assertEqual(response.status_code, 302)

        person = Person.objects.get(username='kgtestuser3')

        self.assertEqual(person.is_active, False)
        self.assertEqual(person.projects.count(), 0)
        self.assertEqual(person.account_set.count(), 1)
        self.assertEqual(person.account_set.all()[0].date_deleted,
                         datetime.date.today())
        self.assertRaises(
            self._datastore._account.DoesNotExist,
            self._datastore._accounts().get,
            uid='kgtestuser3')

        # Test activating
        response = self.client.post(
            reverse('kg_person_activate', args=[person.username]))
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(username='kgtestuser3')
        self.assertEqual(person.is_active, True)

    def stest_delete_account(self):
        person = Person.objects.get(pk=Person.objects.count())
        ua = person.account_set.all()[0]
        self.assertEqual(person.is_active, True)
        self.assertEqual(person.account_set.count(), 1)
        self.assertEqual(ua.date_deleted, None)

        response = self.client.post(
            '/%susers/accounts/delete/%i/' % (settings.BASE_URL, ua.id))
        self.assertEqual(response.status_code, 302)

        person = Person.objects.get(pk=Person.objects.count())
        ua = person.account_set.all()[0]
        self.assertEqual(ua.date_deleted, datetime.date.today())
        self.assertEqual(person.project_set.count(), 0)

    def stest_default_projects(self):

        person = Person.objects.get(pk=Person.objects.count())
        ua = person.account_set.all()[0]

        self.assertEqual(person.project_set.count(), 1)
        self.assertEqual(person.project_set.all()[0], ua.default_project)
        project = Project.objects.create(
            pid='test2',
            name='test project',
            leader=person,
            start_date=datetime.date.today(),
            machine_category=MachineCategory.objects.get(name='VPAC'),
            institute=Institute.objects.get(name='VPAC'),
            is_active=True,
            is_approved=True,
        )
        project.users.add(person)
        self.assertEqual(person.project_set.count(), 2)
        # change default
        response = self.client.post(
            reverse('kg_account_set_default', args=[ua.id, project.pid]))

        self.assertEqual(response.status_code, 302)

        person = Person.objects.get(pk=Person.objects.count())
        ua = person.account_set.all()[0]
        project = Project.objects.get(pid='test2')

        self.assertEqual(person.project_set.count(), 2)
        self.assertEqual(project, ua.default_project)

    def stest_add_user_to_project(self):

        person = Person.objects.get(pk=Person.objects.count())
        person.account_set.all()[0]

        self.assertEqual(person.project_set.count(), 1)

        Project.objects.create(
            pid='test2',
            name='test project 5',
            leader=Person.objects.get(username='leader'),
            start_date=datetime.date.today(),
            machine_category=MachineCategory.objects.get(name='VPAC'),
            institute=Institute.objects.get(name='VPAC'),
            is_active=True,
            is_approved=True,
        )

        response = self.client.post(
            reverse('kg_person_detail', args=[person.username]),
            {'project': 'test2', 'project-add': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(person.project_set.count(), 2)

    def test_password_reset_by_self(self):
        logged_in = self.client.login(
            username='kgtestuser1', password='aq12ws')
        self.assertEqual(logged_in, True)

        if django.VERSION >= (1, 9):
            url_prefix = ""
        else:
            url_prefix = 'http://testserver'

        # send request
        url = reverse("kg_profile_reset")
        done_url = reverse("kg_profile_reset_done")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0],
                         url_prefix + done_url)

        # check email
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "TestOrg Password change")
        url = re.search("(?P<url>https?://[^\s]+)", message.body).group("url")
        self.assertTrue(
            url.startswith("https://example.com/users/persons/reset/"))
        url = url[25:]

        # get password reset page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # send new password
        form_data = {
            'new_password1': 'q1w2e3r4',
            'new_password2': 'q1w2e3r4',
        }
        done_url = reverse("password_reset_complete")
        response = self.client.post(url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0],
                         url_prefix + done_url)

        # test new password
        logged_in = self.client.login(
            username='kgtestuser1', password='q1w2e3r4')
        self.assertEqual(logged_in, True)

    def test_password_reset_by_admin(self):
        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.assertEqual(logged_in, True)

        if django.VERSION >= (1, 9):
            url_prefix = ""
        else:
            url_prefix = 'http://testserver'

        # send request
        url = reverse("kg_person_reset", args=["kgtestuser1"])
        done_url = reverse("kg_person_reset_done", args=["kgtestuser1"])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0],
                         url_prefix + done_url)
        self.client.logout()

        # check email
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "TestOrg Password change")
        url = re.search("(?P<url>https?://[^\s]+)", message.body).group("url")
        self.assertTrue(
            url.startswith("https://example.com/users/persons/reset/"))
        url = url[25:]

        # get password reset page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # send new password
        form_data = {
            'new_password1': 'q1w2e3r4',
            'new_password2': 'q1w2e3r4',
        }
        done_url = reverse("password_reset_complete")
        response = self.client.post(url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0],
                         url_prefix + done_url)

        # test new password
        logged_in = self.client.login(
            username='kgtestuser1', password='q1w2e3r4')
        self.assertEqual(logged_in, True)
