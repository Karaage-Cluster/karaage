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

from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models.related import RelatedObject
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

import datetime

from karaage.constants import TITLES, COUNTRIES
from karaage.util import new_random_token, get_current_person
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Account


class Application(models.Model):
    """ Generic application for anything. """

    NEW = 'N'
    OPEN = 'O'
    WAITING_FOR_LEADER = 'L'
    WAITING_FOR_ADMIN = 'K'
    PASSWORD = 'P'
    COMPLETED = 'C'
    ARCHIVED = 'A'
    DECLINED = 'R'

    APPLICATION_STATES = (
        (NEW, 'Invitiation Sent'),
        (OPEN, 'Open'),
        (WAITING_FOR_LEADER, 'Waiting for project leader approval'),
        (WAITING_FOR_ADMIN, 'Waiting for Karaage admin approval'),
        (PASSWORD, 'Applicant needs to set password'),
        (COMPLETED, 'Complete'),
        (ARCHIVED, 'Archived'),
        (DECLINED, 'Declined'),
        )

    secret_token = models.CharField(max_length=64, default=new_random_token, editable=False, unique=True)
    expires = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(Person, editable=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=1, choices=APPLICATION_STATES)
    complete_date = models.DateTimeField(null=True, blank=True, editable=False)
    content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in': ['person', 'applicant']}, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    applicant = generic.GenericForeignKey()
    header_message = models.TextField('Message', null=True, blank=True, help_text=u"Message displayed at top of application form for the invitee and also in invitation email")
    _class = models.CharField(max_length=100, editable=False)

    def __unicode__(self):
        return "Application #%s" % self.id

    def info(self):
        return unicode(self)

    def get_type(self):
        return self._class

    @models.permalink
    def get_absolute_url(self):
        return ('kg_application_detail', [self.id])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = get_current_person()
            self.expires = datetime.datetime.now() + datetime.timedelta(days=7)
            parent = self._meta.parents.keys()[0]
            subclasses = parent._meta.get_all_related_objects()
            for klass in subclasses:
                if isinstance(klass, RelatedObject) and klass.field.primary_key and klass.opts == self._meta:
                    self._class = klass.get_accessor_name()
                    break
        return super(Application, self).save(*args, **kwargs)
    save.alters_data = True

    def delete(self):
        if self.content_type and self.content_type.model == 'applicant':
            if self.applicant.applications.count() <= 1:
                self.applicant.delete()
        super(Application, self).delete()
    delete.alters_data = True

    def get_object(self):
        try:
            if self._class and self._meta.get_field_by_name(self._class)[0].opts != self._meta:
                return getattr(self, self._class)
        except FieldDoesNotExist:
            pass
        return self

    def reopen(self):
        self.created_by = get_current_person()
        self.submitted_date = None
        self.complete_date = None
        self.save()

    def submit(self):
        self.submited_date = datetime.datetime.now()
        self.save()

    def approve(self):
        assert self.applicant is not None
        if self.content_type.model == 'applicant':
            person = self.applicant.approve()
            created_person = True
        elif self.content_type.model == 'person' :
            person = self.applicant
            created_person = False
        else:
            assert False
        self.applicant = person
        self.complete_date = datetime.datetime.now()
        self.save()
        return created_person
    approve.alters_data = True

    def decline(self):
        self.complete_date = datetime.datetime.now()
        self.save()
    decline.alters_data = True

class UserApplication(Application):
    """ Application for an Applicant or a Person to join an existing project. """
    project = models.ForeignKey(Project, null=True, blank=True, limit_choices_to={'is_active': True})
    needs_account = models.BooleanField(u"Do you need a personal cluster account?", help_text=u"Required if you will be working on the project yourself.", default=True)
    make_leader = models.BooleanField(help_text="Make this person a project leader")

    def info(self):
        if self.project is None:
            return "to join unspecified project"
        else:
            return "to join project %s" % self.project

    def submit(self):
        super(UserApplication, self).submit()

    def approve(self):
        created_person = super(UserApplication, self).approve()
        assert self.applicant is not None
        assert self.content_type.model == "person"
        person = self.applicant
        if self.make_leader:
            self.project.leaders.add(person)
        self.save()
        created_account = False
        if self.needs_account:
            for mc in self.project.machine_categories.all():
                if not person.has_account(mc):
                    Account.create(person, project, mc)
                    created_account = True
        self.project.group.members.add(person)
        return created_person, created_account
    approve.alters_data = True

    def authenticate(self, person):
        auth = {}

        auth['is_applicant'] = False
        if person == self.applicant:
            auth['is_applicant'] = True

        auth['is_leader'] = False
        if self.project is not None:
            if person in self.project.leaders.all():
                auth['is_leader'] = True
        return auth


class ProjectApplication(Application):
    """ Application for an Applicant or a Person to create a new project. """
    name = models.CharField('Title', max_length=200)
    institute = models.ForeignKey(Institute, limit_choices_to={'is_active': True}, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)
    needs_account = models.BooleanField(u"Do you need a personal cluster account?", help_text=u"Required if you will be working on the project yourself.", default=True)
    machine_categories = models.ManyToManyField(MachineCategory, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    pid = models.CharField(max_length=50, null=True, blank=True)

    def info(self):
        if self.name is None:
            return "to create unspecified project"
        else:
            return "to create project %s" % self.name

    def submit(self):
        self.institute = self.applicant.institute
        super(ProjectApplication, self).submit()

    def approve(self, pid=None):
        created_person = super(ProjectApplication, self).approve()
        assert self.applicant is not None
        assert self.institute is not None
        assert self.content_type.model == "person"
        person = self.applicant
        from karaage.projects.utils import add_user_to_project, get_new_pid
        project = Project(
            pid=self.pid or get_new_pid(self.institute),
            name=self.name,
            description=self.description,
            institute=self.institute,
            additional_req=self.additional_req,
            start_date=datetime.datetime.today(),
            end_date=datetime.datetime.today() + datetime.timedelta(days=365),
            )
        project.save()
        project.leaders.add(person)
        for mc in self.machine_categories.all():
            project.machine_categories.add(mc)
        project.activate()
        self.project = project
        self.save()
        created_account = False
        if self.needs_account:
            for mc in self.project.machine_categories.all():
                if not person.has_account(mc):
                    Account.create(person, project, mc)
                    created_account = True
        self.project.group.members.add(person)
        return created_person, created_account
    approve.alters_data = True

    def authenticate(self, person):
        auth = {}

        auth['is_applicant'] = False
        if person == self.applicant:
            auth['is_applicant'] = True

        auth['is_leader'] = False
        if self.institute is not None:
            if person in self.institute.delegates.all():
                auth['is_leader'] = True

        return auth


class Applicant(models.Model):
    """ A person who has completed an application however is not yet officially
    registered on the system yet. """
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(editable=False)
    username = models.CharField(max_length=16, unique=True, help_text="Required. 16 characters or fewer. Letters, numbers and underscores only", null=True, blank=True)
    title = models.CharField(choices=TITLES, max_length=10, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    institute = models.ForeignKey(Institute, help_text="If your institute is not listed please contact %s" % settings.ACCOUNTS_EMAIL, limit_choices_to={'is_active': True}, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField("Office Telephone", max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    supervisor = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    saml_id = models.CharField(max_length=200, null=True, blank=True, editable=False)
    applications = generic.GenericRelation(Application)

    def __unicode__(self):
        if self.first_name:
            return self.get_full_name()
        return self.email

    def has_account(self, mc):
        return False

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def approve(self):
        person = Person.create_from_applicant(self)
        person.activate()
        for application in self.applications.all():
            application.applicant = person
            application.save()
        self.delete()
        return person
    approve.alters_data = True
