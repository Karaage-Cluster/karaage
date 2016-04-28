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

import six

from django.db import models
from django.db.models import Q

try:
    # Django < 1.8
    from django.db.models.related import RelatedObject as OneToOneRel
except ImportError:
    # Django >= 1.8
    from django.db.models.fields.related import OneToOneRel

from django.contrib.contenttypes.models import ContentType
try:
    # Django >= 1.7
    from django.contrib.contenttypes.fields import GenericForeignKey, \
        GenericRelation
except ImportError:
    # Django < 1.7
    from django.contrib.contenttypes.generic import GenericForeignKey, \
        GenericRelation
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

import datetime

from model_utils import FieldTracker

from karaage.common.constants import TITLES, COUNTRIES
from karaage.common import new_random_token, get_current_person, is_admin, log
from karaage.people.models import Person
from karaage.institutes.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory, Account


class ApplicationManager(models.Manager):

    def get_for_applicant(self, person):
        query = self.get_queryset()
        query = query.filter(content_type__model="person", object_id=person.pk)
        query = query.exclude(state__in=[
            Application.COMPLETED, Application.ARCHIVED, Application.DECLINED])
        return query

    def requires_attention(self, request):
        person = request.user
        query = Q(
            projectapplication__project__in=person.leads.all(),
            state=ProjectApplication.WAITING_FOR_LEADER)
        query = query | Q(
            projectapplication__institute__in=person.delegate_for.all(),
            state=ProjectApplication.WAITING_FOR_DELEGATE)
        if is_admin(request):
            query = query | Q(state=Application.WAITING_FOR_ADMIN)
            query = query | Q(
                state=ProjectApplication.DUPLICATE,
                projectapplication__isnull=False)
        return self.get_queryset().filter(query)


@python_2_unicode_compatible
class Application(models.Model):

    """ Generic application for anything. """
    WAITING_FOR_ADMIN = 'K'
    COMPLETED = 'C'
    ARCHIVED = 'A'
    DECLINED = 'R'

    secret_token = models.CharField(
        max_length=64, default=new_random_token, editable=False, unique=True)
    expires = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(
        Person, editable=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=5)
    complete_date = models.DateTimeField(null=True, blank=True, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to={'model__in': ['person', 'applicant']},
        null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    applicant = GenericForeignKey()
    header_message = models.TextField(
        'Message', null=True, blank=True,
        help_text=six.u(
            "Message displayed at top of application form "
            "for the invitee and also in invitation email"))
    _class = models.CharField(max_length=100, editable=False)

    objects = ApplicationManager()

    _tracker = FieldTracker()

    class Meta:
        db_table = "applications_application"

    def __str__(self):
        return "Application #%s" % self.id

    def info(self):
        return six.text_type(self)

    def get_type(self):
        return self._class

    @models.permalink
    def get_absolute_url(self):
        return 'kg_application_detail', [self.id]

    def save(self, *args, **kwargs):
        created = self.pk is None
        if not self.expires:
            self.expires = datetime.datetime.now() + datetime.timedelta(days=7)
        if not self.pk:
            self.created_by = get_current_person()

            # Find the accessor from Application to type(self) class
            if hasattr(Application._meta, 'get_fields'):
                # Django >= 1.8
                fields = [
                    f for f in Application._meta.get_fields()
                    if isinstance(f, OneToOneRel) and
                    f.field.primary_key and
                    f.auto_created
                ]

            else:
                # Django <= 1.8
                fields = [
                    f for f in Application._meta.get_all_related_objects()
                    if isinstance(f, OneToOneRel) and
                    f.field.primary_key
                ]

            for rel in fields:
                # Works with Django < 1.8 and => 1.8
                related_model = getattr(rel, 'related_model', rel.model)

                # if we find it, save the name
                if related_model == type(self):
                    self._class = rel.get_accessor_name()
                    break

        super(Application, self).save(*args, **kwargs)

        if created:
            log.add(self, 'Created')
        for field in self._tracker.changed():
            log.change(
                self,
                'Changed %s to %s' % (field, getattr(self, field)))
    save.alters_data = True

    def delete(self, *args, **kwargs):
        log.delete(self, 'Deleted')
        super(Application, self).delete(*args, **kwargs)

    def get_object(self):
        if self._class:
            return getattr(self, self._class)
        return self

    def reopen(self):
        self.submitted_date = None
        self.complete_date = None
        self.expires = datetime.datetime.now() + datetime.timedelta(days=7)
        self.save()

    def extend(self):
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
        elif self.content_type.model == 'person':
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

    def check_valid(self):
        errors = []

        if self.applicant is None:
            errors.append("Applicant not set.")
        elif self.content_type.model == 'applicant':
            errors.extend(self.applicant.check_valid())

        return errors

    def get_roles_for_person(self, person):
        roles = set()

        if person == self.applicant:
            roles.add('is_applicant')
            roles.add('is_authorised')

        return roles


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
    needs_account = models.BooleanField(
        six.u("Do you need a personal cluster account?"),
        help_text=six.u(
            "Required if you will be working on the project yourself."),
        default=True)
    make_leader = models.BooleanField(
        help_text="Make this person a project leader", default=False)

    # new project request
    name = models.CharField('Title', max_length=200)
    institute = models.ForeignKey(
        Institute, limit_choices_to={'is_active': True}, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)
    machine_categories = models.ManyToManyField(
        MachineCategory, blank=True)
    pid = models.CharField(max_length=50, null=True, blank=True)

    # existing project request
    project = models.ForeignKey(Project, null=True, blank=True)

    objects = ApplicationManager()

    class Meta:
        db_table = "applications_projectapplication"

    def info(self):
        if self.project is not None:
            return six.u("join project '%s'") % self.project.pid
        elif self.name:
            return six.u("create project '%s'") % self.name
        else:
            return six.u("create/join a project")

    def approve(self, approved_by):
        created_person, created_account = \
            super(ProjectApplication, self).approve(approved_by)
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
                end_date=datetime.datetime.today() +
                datetime.timedelta(days=365),
            )
            project.save()
            for mc in self.machine_categories.all():
                project.projectquota_set.create(machine_category=mc)
            project.activate(approved_by)
            self.project = project
            self.save()
        if self.make_leader:
            self.project.leaders.add(person)
        if self.needs_account:
            found_pc = False
            for pc in self.project.projectquota_set.all():
                found_pc = True
                if not person.has_account(pc.machine_category):
                    log.add(
                        self.application_ptr,
                        'Created account on machine category %s'
                        % pc.machine_category)
                    Account.create(person, self.project, pc.machine_category)
                    created_account = True
                else:
                    log.change(
                        self.application_ptr,
                        'Account on machine category %s already exists'
                        % pc.machine_category)
            if not found_pc:
                log.change(
                    self.application_ptr,
                    'No project quotas found; no accounts created '
                    'despite being requested')
        self.project.group.members.add(person)
        return created_person, created_account
    approve.alters_data = True

    def get_roles_for_person(self, person):
        roles = super(ProjectApplication, self).get_roles_for_person(person)

        if self.project is not None:
            if person in self.project.leaders.all():
                roles.add('is_leader')
                roles.add('is_authorised')

        if self.institute is not None:
            if person in self.institute.delegates.all():
                roles.add('is_delegate')
                roles.add('is_authorised')

        return roles

    def check_valid(self):
        errors = super(ProjectApplication, self).check_valid()

        if self.project is None:
            if not self.name:
                errors.append(
                    "New project application with no name")
            if self.institute is None:
                errors.append(
                    "New project application with no institute")

        return errors


@python_2_unicode_compatible
class Applicant(models.Model):

    """ A person who has completed an application however is not yet officially
    registered on the system yet. """
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(editable=False, default=False)
    username = models.CharField(max_length=255, unique=True,
                                null=True, blank=True)
    title = models.CharField(
        choices=TITLES, max_length=10, null=True, blank=True)
    short_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=60)
    institute = models.ForeignKey(
        Institute,
        help_text="If your institute is not listed please contact %s"
        % settings.ACCOUNTS_EMAIL,
        limit_choices_to={'is_active': True},
        null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField(
        "Office Telephone", max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    supervisor = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    country = models.CharField(
        max_length=2, choices=COUNTRIES, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    saml_id = models.CharField(
        max_length=200, null=True, blank=True, editable=False, unique=True)
    applications = GenericRelation(Application)

    class Meta:
        db_table = "applications_applicant"

    def __str__(self):
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

    def check_valid(self):
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
            'is_active': False,
        }
        person = Person.objects.create_user(**data)
        person.activate(approved_by)

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
