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
from django.conf import settings
from django.core.management import call_command

from tldap.test import slapd
from captcha.models import CaptchaStore
from karaage.applications.models import Application, Applicant
from karaage.people.models import Person, Institute
from karaage.projects.models import Project
from karaage.test_data.initial_ldap_data import test_ldif


class UserApplicationTestCase(TestCase):
    urls = 'testproject.registration_urls'

    def setUp(self):
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        call_command('loaddata', 'karaage_data', **{'verbosity': 0})

        self.server = server

    def tearDown(self):
        self.server.stop()


    def test_register_account(self):
        self.assertEquals(len(mail.outbox), 0)
        response = self.client.get(reverse('kg_new_userapplication'))
        self.failUnlessEqual(response.status_code, 200)
        hash_ = response.content[response.content.find('name="captcha_0" value="')+24:response.content.find('name="captcha_0" value="')+64]

        try:
            captcha_text = CaptchaStore.objects.get(hashkey=hash_).response
        except:
            self.fail()

        form_data = {
            'title' : 'Mr',
            'first_name': 'Jim',
            'last_name': 'Bob',
            'position': 'Researcher',
            'institute': 1,
            'department': 'Maths',
            'email': 'jim.bob@example.com',
            'telephone': '4444444',
            'username': 'jimbob',
            'password1': 'Exaiquouxei0',
            'password2': 'Exaiquouxei0',
            'aup': True,
            'captcha_0': hash_,
            'captcha_1': captcha_text,
        }

        response = self.client.post(reverse('kg_new_userapplication'), form_data, follow=True)
        token = Application.objects.all()[0].secret_token
        self.failUnlessEqual(response.redirect_chain[0][0], 'http://testserver' + reverse('kg_application_choose_project', args=[token,]))
        self.failUnlessEqual(response.status_code, 200)
        form_data = {
            'project': 'TestProject1',
            }

        response = self.client.post(reverse('kg_application_choose_project', args=[token,]), form_data, follow=True)
        
        applicant = Applicant.objects.get(username='jimbob')
        application = applicant.applications.all()[0]
        self.failUnlessEqual(response.redirect_chain[0][0], 'http://testserver' + reverse('kg_application_done', args=[application.secret_token]))
        self.failUnlessEqual(response.status_code, 200)

        self.failUnlessEqual(application.state, Application.WAITING_FOR_LEADER)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'TestOrg Project join request')
        self.assertEquals(mail.outbox[0].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[0].to[0], 'leader@example.com')

        # Leader logs in to approve      
        logged_in = self.client.login(username='kgtestuser1', password='aq12ws')
        self.failUnlessEqual(logged_in, True)
        
        response = self.client.get(reverse('kg_userapplication_detail', args=[application.id]))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.post(reverse('kg_userapplication_detail', args=[application.id]))
        self.failUnlessEqual(response.status_code, 302)

        application = Application.objects.get(pk=application.id)
        self.failUnlessEqual(application.state, Application.WAITING_FOR_ADMIN)

        self.assertEquals(len(mail.outbox), 2)
        


class AdminRegistrationTestCase(TestCase):

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        call_command('loaddata', 'karaage_data', **{'verbosity': 0})

        self.server = server

    def tearDown(self):
        self.server.stop()

    def stest_admin_approve_account(self):
        from karaage.datastores import create_new_user

        logged_in = self.client.login(username='kgsuper', password='aq12ws')
        self.failUnlessEqual(logged_in, True)
        project = Project.objects.get(pid='TestProject1')
        project.users.count()
        
        institute = Institute.objects.get(pk=1)
        
        person_data = {
            'title' : 'Mr',
            'first_name': 'Jim',
            'last_name': 'Bob',
            'position': 'Researcher',
            'institute': institute,
            'department': 'Maths',
            'email': 'jim.bob@example.com',
            'country': 'AU',
            'telephone': '4444444',
            'username': 'jimbob',
            'password1': 'Exaiquouxei0',
            'password2': 'Exaiquouxei0',
        }
        person = create_new_user(person_data)
        
        join_request = ProjectJoinRequest.objects.create(
            person=person,
            project=project,
            leader_approved=True,
            )
        lcon = LDAPClient()
        self.failUnlessRaises(placard_exceptions.DoesNotExistException, lcon.get_user, 'uid=jimbob')
        self.failUnlessEqual(person.is_active, False)

        response = self.client.get(reverse('kg_account_request_detail', args=[join_request.id]))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 0)
        response = self.client.post(reverse('kg_account_approve', args=[join_request.id]))
        self.failUnlessEqual(response.status_code, 302)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'TestOrg Account approval')
        self.assertEquals(mail.outbox[0].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[0].to[0], 'jim.bob@example.com')

        self.failUnlessRaises(ProjectJoinRequest.DoesNotExist, ProjectJoinRequest.objects.get, pk=join_request.id)
        person = Person.objects.get(username='jimbob')
        self.failUnlessEqual(person.is_active, True)

        luser = lcon.get_user('uid=jimbob')
        self.assertEqual(luser.givenName, 'Jim')


class ProjectRegistrationTestCase(TestCase):
    urls = 'testproject.registration_urls'

    def setUp(self):
        global server
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        call_command('loaddata', 'karaage_data', **{'verbosity': 0})

        self.server = server

    def tearDown(self):
        self.server.stop()


    def stest_register_project(self):
        self.assertEquals(len(mail.outbox), 0)
        response = self.client.get(reverse('project_registration'))
        self.failUnlessEqual(response.status_code, 200)
        hash_ = response.content[response.content.find('name="captcha_0" value="')+24:response.content.find('name="captcha_0" value="')+64]

        try:
            captcha_text = CaptchaStore.objects.get(hashkey=hash_).response
        except:
            self.fail()

        form_data = {
            'title' : 'Mr',
            'first_name': 'Jim',
            'last_name': 'Bob',
            'position': 'Researcher',
            'institute': 1,
            'department': 'Maths',
            'email': 'jim.bob@example.com',
            'country': 'AU',
            'telephone': '4444444',
            'username': 'jimbob',
            'password1': 'Exaiquouxei0',
            'password2': 'Exaiquouxei0',
            'needs_account': True,
            'project_name': 'Lasers',
            'project_institute': 1,
            'project_description': 'Lasers are cool',
            'tos': True,
            'captcha_0': hash_,
            'captcha_1': captcha_text,
        }
        response = self.client.post(reverse('project_registration'), form_data, follow=True)
        
        project_request = ProjectCreateRequest.objects.get(pk=1)

        self.failUnlessEqual(response.redirect_chain[0][0], 'http://testserver' + reverse('project_created', args=[project_request.id]))
        self.failUnlessEqual(response.status_code, 200)
     
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'TestOrg new project request')
        self.assertEquals(mail.outbox[0].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[0].to[0], 'leader@example.com')

        person = Person.objects.get(username='jimbob')

        self.failUnlessEqual(project_request.needs_account, True)
        self.failUnlessEqual(person.is_active, False)
 
        project = Project.objects.get(name='Lasers')
        self.failUnlessEqual(project.is_active, False)
        self.failUnlessEqual(project.pid, 'pExam0001')
        self.failUnlessEqual(project.projectcreaterequest_set.all()[0], person.projectcreaterequest_set.all()[0])
        lcon = LDAPClient()
        lgroup = lcon.get_group('cn=%s' % project.pid)
        self.failUnlessEqual(lgroup.cn, project.pid)

        # Delegate logs in to approve      
        logged_in = self.client.login(username='kgtestuser1', password='aq12ws')
        self.failUnlessEqual(logged_in, True)
        
        response = self.client.get(reverse('user_project_request_detail', args=[project_request.id]))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(len(mail.outbox), 1)
        response = self.client.post(reverse('user_approve_project', args=[project_request.id]))
        self.failUnlessEqual(response.status_code, 302)

        self.failUnlessRaises(ProjectCreateRequest.DoesNotExist, ProjectCreateRequest.objects.get, pk=project_request.id)

        project = Project.objects.get(name='Lasers')
        self.failUnlessEqual(project.is_active, True)
        self.failUnlessEqual(project.users.all()[0], person)

        lgroup = lcon.get_group('cn=%s' % project.pid)
        lgroup_members = lcon.get_group_members('cn=%s' % project.pid)
        self.failUnlessEqual(lgroup_members[0].uid, project.users.all()[0].username)
        self.failUnlessEqual(lgroup.cn, project.pid)

        person = Person.objects.get(username='jimbob')
        self.failUnlessEqual(person.is_active, True)
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[1].subject, 'TestOrg Project has been approved')
        self.assertEquals(mail.outbox[1].from_email, settings.ACCOUNTS_EMAIL)
        self.assertEquals(mail.outbox[1].to[0], 'jim.bob@example.com')
