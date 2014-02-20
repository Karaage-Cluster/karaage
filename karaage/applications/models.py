# Copyright 2007-2013 VPAC
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
from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django.db.models.related import RelatedObject
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

import datetime
import warnings

from model_utils import FieldTracker

from karaage.common.constants import TITLES, COUNTRIES
from karaage.common import new_random_token, get_current_person, is_admin, log
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Account
from karaage.software.models import SoftwareLicenseAgreement

class ApplicationManager(models.Manager):
    def get_for_applicant(self, person):
        ct = ContentType.objects.get(model='person')
        query = Application.objects.filter(content_type=ct, object_id=person.pk).exclude(
                state__in=[Application.COMPLETED, Application.ARCHIVED, Application.DECLINED])
        return query

    def requires_attention(self, request):
        person = request.user
        query = Q(projectapplication__project__in=person.leaders.all(), state=ProjectApplication.WAITING_FOR_LEADER)
        query = query | Q(projectapplication__institute__in=person.delegate.all(), state=ProjectApplication.WAITING_FOR_DELEGATE)
        if is_admin(request):
            query = query | Q(state=Application.WAITING_FOR_ADMIN)
            query = query | Q(state=ProjectApplication.DUPLICATE, projectapplication__isnull=False)
        return Application.objects.filter(query)


class Application(models.Model):
    """ Generic application for anything. """
    WAITING_FOR_ADMIN = 'K'
    COMPLETED = 'C'
    ARCHIVED = 'A'
    DECLINED = 'R'

    secret_token = models.CharField(max_length=64, default=new_random_token, editable=False, unique=True)
    expires = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(Person, editable=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=5)
    complete_date = models.DateTimeField(null=True, blank=True, editable=False)
    content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in': ['person', 'applicant']}, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    applicant = generic.GenericForeignKey()
    header_message = models.TextField('Message', null=True, blank=True, help_text=u"Message displayed at top of application form for the invitee and also in invitation email")
    _class = models.CharField(max_length=100, editable=False)

    objects = ApplicationManager()

    _tracker = FieldTracker()

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

        for field in self._tracker.changed():
            log(None, self, 2, 'Changed %s to %s' % (field,  getattr(self, field)))

        return super(Application, self).save(*args, **kwargs)
    save.alters_data = True

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
        self.expires = datetime.datetime.now() + datetime.timedelta(days=7)
        self.save()

    def submit(self):
        self.submitted_date = datetime.datetime.now()
        self.save()

    def approve(self, approved_by):
        assert self.applicant is not None
        if self.content_type.model == 'applicant':
            person = self.applicant.approve(approved_by)
            created_person = True
        elif self.content_type.model == 'person' :
            person = self.applicant
            created_person = False
        else:
            assert False
        self.applicant = person
        self.complete_date = datetime.datetime.now()
        self.save()
        return created_person, False
    approve.alters_data = True

    def decline(self):
        self.complete_date = datetime.datetime.now()
        self.save()
    decline.alters_data = True

    def check(self):
        errors = []

        if self.applicant is None:
            errors.append("Applicant not set.")
        elif self.content_type.model == 'applicant':
            errors.extend(self.applicant.check())

        return errors


class ProjectApplication(Application):
    type = "project"

    OPEN = 'O'
    WAITING_FOR_LEADER = 'L'
    WAITING_FOR_DELEGATE = 'D'
    PASSWORD = 'P'
    DUPLICATE = 'DUP'

    """ Application for an Applicant or a Person to create a new project or
    join an existing project. """
    # common properties
    needs_account = models.BooleanField(u"Do you need a personal cluster account?", help_text=u"Required if you will be working on the project yourself.", default=True)

    # new project request
    name = models.CharField('Title', max_length=200)
    institute = models.ForeignKey(Institute, limit_choices_to={'is_active': True}, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)
    machine_categories = models.ManyToManyField(MachineCategory, null=True, blank=True)
    pid = models.CharField(max_length=50, null=True, blank=True)

    # existing project request
    project = models.ForeignKey(Project, null=True, blank=True)
    make_leader = models.BooleanField(help_text="Make this person a project leader", default=False)

    def info(self):
        if self.project is not None:
            return u"join project '%s'" % self.project.pid
        elif self.name:
            return u"create project '%s'" % self.name
        else:
            return u"create/join a project"

    def approve(self, approved_by):
        created_person, created_account = super(ProjectApplication, self).approve(approved_by)
        created_project = False
        assert self.applicant is not None
        assert self.content_type.model == "person"
        person = self.applicant
        if self.project is None:
            assert self.institute is not None
            from karaage.projects.utils import get_new_pid
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
                project.projectquota_set.create(machine_category=mc)
            project.activate(approved_by)
            self.project = project
            self.save()
            created_project = True
        if self.needs_account:
            for pc in self.project.projectquota_set.all():
                if not person.has_account(pc.machine_category):
                    Account.create(person, self.project, pc.machine_category)
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

        auth['is_delegate'] = False
        if self.institute is not None:
            if person in self.institute.delegates.all():
                auth['is_delegate'] = True

        return auth

    def check(self):
        errors = super(ProjectApplication, self).check()

        if self.project is None:
            if not self.name:
                errors.append(
                "New project application with no name")
            if self.institute is None:
                errors.append(
                "New project application with no institute")

        return errors



class SoftwareApplication(Application):
    type = "software"
    software_license = models.ForeignKey('software.SoftwareLicense')

    def info(self):
        return u"access %s" % self.software_license.software

    def authenticate(self, person):
        auth = {}

        auth['is_applicant'] = False
        if person == self.applicant:
            auth['is_applicant'] = True

        return auth

    def check(self):
        errors = super(SoftwareApplication, self).check()

        if self.content_type.model != 'person':
            errors.append("Applicant not already registered person.")

        return errors

    def approve(self, approved_by):
        created_person = super(SoftwareApplication, self).approve(approved_by)

        try:
            sla = SoftwareLicenseAgreement.objects.get(
                user=self.applicant,
                license=self.software_license,
            )
        except SoftwareLicenseAgreement.DoesNotExist:
            sla = SoftwareLicenseAgreement()
            sla.user = self.applicant
            sla.license = self.software_license
            sla.date = datetime.datetime.today()
            sla.save()

        self.software_license.software.group.add_person(self.applicant)
        return created_person


class Applicant(models.Model):
    """ A person who has completed an application however is not yet officially
    registered on the system yet. """
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(editable=False, default=False)
    username = models.CharField(max_length=16, unique=True, help_text="Required. 16 characters or fewer. Letters, numbers and underscores only", null=True, blank=True)
    title = models.CharField(choices=TITLES, max_length=10, null=True, blank=True)
    short_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=60)
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
    saml_id = models.CharField(max_length=200, null=True, blank=True, editable=False, unique=True)
    applications = generic.GenericRelation(Application)

    def __unicode__(self):
        full_name = self.get_full_name()
        if full_name:
            return full_name
        return self.email

    def has_account(self, mc):
        return False

    def get_full_name(self):
        """ Get the full name of the person. """
        return self.full_name

    def get_short_name(self):
        """ Get the abbreviated name of the person. """
        return self.short_name

    def check(self):
        errors = []

        if not self.username:
            errors.append("Username not completed")
        if not self.short_name:
            errors.append("Short name not completed")
        if not self.full_name:
            errors.append("Full name not completed")
        if not self.email:
            errors.append("EMail not completed")

        # check for username conflict
        query = Person.objects.filter(username=self.username)
        if self.username and query.count() > 0:
            errors.append(
                    "Application username address conflicts "
                    "with existing person.")

        # check for saml_id conflict
        query = Person.objects.filter(saml_id=self.saml_id)
        if self.saml_id and query.count() > 0:
            errors.append(
                    "Application saml_id address conflicts "
                    "with existing person.")

        # check for email conflict
        query = Person.objects.filter(email=self.email)
        if self.email and query.count() > 0:
            errors.append(
                    "Application email address conflicts "
                    "with existing person.")

        return errors

    def approve(self, approved_by):
        """ Create a new user from an applicant. """
        data = {
            'email': self.email,
            'username': self.username,
            'title': self.title,
            'short_name': self.short_name,
            'full_name': self.full_name,
            'institute': self.institute,
            'department': self.department,
            'position': self.position,
            'telephone': self.telephone,
            'mobile': self.mobile,
            'supervisor': self.supervisor,
            'address': self.address,
            'city': self.city,
            'postcode': self.postcode,
            'country': self.country,
            'fax': self.fax,
            'saml_id': self.saml_id,
            'approved_by': approved_by,
            }
        person = Person.objects.create_user(**data)

        for application in self.applications.all():
            application.applicant = person
            application.save()
        self.delete()
        return person
    approve.alters_data = True

    def similar_people(self):
        term = False
        query = Q()
        if self.username:
            query = query | Q(username__iexact=self.username)
            term = True
        if self.saml_id:
            query = query | Q(saml_id=self.saml_id)
            term = True
        if self.email:
            query = query | Q(email__iexact=self.email)
            term = True
        if self.short_name:
            query = query | Q(full_name__iexact=self.short_name)
            term = True
        if self.full_name:
            query = query | Q(full_name__iexact=self.full_name)
            term = True
        if not term:
            return Person.objects.none()
        return Person.objects.filter(query)
