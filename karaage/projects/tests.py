from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.core.urlresolvers import reverse

import datetime

from karaage.people.models import Person, Institute
from karaage.machines.models import MachineCategory, UserAccount
from karaage.tests.util import fill_database

from models import Project


class ProjectTestCase(TestCase):
    fixtures = ['emails', 'sites']

    def setUp(self):
        self.client = Client()
        fill_database()
        project = Project.objects.create(
            pid='project_test',
            name='test project 5',
            leader=Person.objects.get(user__username='leader'),
            start_date = datetime.date.today(),
            machine_category=MachineCategory.objects.get(name='VPAC'),
            institute=Institute.objects.get(name='VPAC'),
            is_active=True,
            is_expertise=True,
            is_approved=True,
        )


    def test_add_project_form_normal(self):
        projects = Project.objects.count()
        
        self.client.login(username='super', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'pid' : 'test4',
            'name': 'Test Project 4',
            'institute': 1,
            'leader': 4,
            'machine_category': 1,
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_add_project'), form_data)

        project = Project.objects.get(pk='test4')
        
        self.failUnlessEqual(response.status_code, 302)

        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(project.approved_by, Person.objects.get(user__username='super'))

    def test_add_project_form_generate(self):
        projects = Project.objects.count()
        
        self.client.login(username='super', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 4',
            'institute': 1,
            'leader': 4,
            'machine_category': 1,
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_add_project'), form_data)

        project = Project.objects.get(pk='pVPAC0001')
        
        self.failUnlessEqual(response.status_code, 302)

        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(project.approved_by, Person.objects.get(user__username='super'))

    def test_add_project_form_generate_expertise(self):
        projects = Project.objects.count()
        
        self.client.login(username='super', password='aq12ws')
        response = self.client.get(reverse('kg_add_project'))
        self.failUnlessEqual(response.status_code, 200)

        form_data = {
            'name': 'Test Project 4',
            'institute': 1,
            'leader': 4,
            'is_expertise': True,
            'machine_category': 1,
            'start_date': datetime.date.today(),
        }

        response = self.client.post(reverse('kg_add_project'), form_data)

        project = Project.objects.get(pk='eppnVPAC0001')
        
        self.failUnlessEqual(response.status_code, 302)

        self.assertEqual(project.is_active, True)
        self.assertEqual(project.date_approved, datetime.date.today())
        self.assertEqual(project.approved_by, Person.objects.get(user__username='super'))
 

    def test_add_remove_user_to_project(self):
        self.client.login(username='super', password='aq12ws')
        project = Project.objects.get(pk='project_test')

        response = self.client.get(reverse('kg_project_detail', args=[project.pid]))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(project.users.count(), 0)

        user = Person.objects.get(user__username='super')
        UserAccount.objects.create(user=user, machine_category=MachineCategory.objects.get(name='VPAC'), date_created=datetime.date.today())
        # add user
        
        response = self.client.post(reverse('kg_project_detail', args=[project.pid]), { 'person': user.id} )
        self.failUnlessEqual(response.status_code, 200)
        project = Project.objects.get(pk='project_test')
        self.assertEqual(project.users.count(), 1)
        
        
        # remove user
        response = self.client.post(reverse('kg_remove_project_member', args=[project.pid, user.username]))
        self.failUnlessEqual(response.status_code, 302)
        project = Project.objects.get(pk='project_test')
        self.assertEqual(project.users.count(), 0)
        
        
    def test_delete_project(self):

        self.client.login(username='super', password='aq12ws')

        project = Project.objects.get(pk='project_test')

        user = Person.objects.get(user__username='super')

        UserAccount.objects.create(user=user, machine_category=MachineCategory.objects.get(name='VPAC'), date_created=datetime.date.today())
        # add user

        response = self.client.post(reverse('kg_project_detail', args=[project.pid]), { 'person': user.id} )

        self.failUnlessEqual(response.status_code, 200)
        project = Project.objects.get(pk='project_test')
        
        self.assertEqual(project.users.count(), 1)
        self.assertEqual(project.is_active, True)
        
        response = self.client.post(reverse('kg_delete_project', args=[project.pid]))
        self.failUnlessEqual(response.status_code, 302)
        
        project = Project.objects.get(pk='project_test')

        self.assertEqual(project.is_active, False)
        self.assertEqual(project.users.count(), 0)
        self.assertEqual(project.date_deleted, datetime.date.today())
        self.assertEqual(project.deleted_by, user)
        
