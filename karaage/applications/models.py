from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models.related import RelatedObject
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

from andsome.middleware.threadlocals import get_current_user

from karaage.constants import TITLES, COUNTRIES
from karaage.util import new_random_token
from karaage.people.models import Person, Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory


class Application(models.Model):
    NEW = 'N'
    OPEN = 'O'
    WAITING_FOR_LEADER = 'L'
    WAITING_FOR_DELEGATE = 'D'
    WAITING_FOR_ADMIN = 'K'
    COMPLETE = 'C'
    APPLICATION_STATES = (
        (NEW, 'Invitiation Sent'),
        (OPEN, 'Open'),
        (WAITING_FOR_LEADER, 'Waiting for project leader approval'),
        (WAITING_FOR_DELEGATE, 'Waiting for institute delegate approval'),
        (WAITING_FOR_ADMIN, 'Waiting for Karaage admin approval'),
        (COMPLETE, 'Complete'),
        )
    
    secret_token = models.CharField(max_length=64, default=new_random_token, editable=False, unique=True)
    expires = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(Person, editable=False, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=1, choices=APPLICATION_STATES, default=NEW)
    content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in': ['person', 'applicant']}, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    applicant = generic.GenericForeignKey()
    header_message = models.TextField('Message', null=True, blank=True, help_text=u"Message displayed at top of application form for the invitee and also in invitation email")
    _class = models.CharField(max_length=100, editable=False)

    def __unicode__(self):
        return "Application #%s" % self.id

    def save(self, *args, **kwargs):
        if not self.pk:
            import datetime
            if get_current_user().is_authenticated():
                self.created_by = get_current_user().get_profile()
            self.expires = datetime.datetime.now() + datetime.timedelta(days=7)
            parent = self._meta.parents.keys()[0]
            subclasses = parent._meta.get_all_related_objects()
            for klass in subclasses:
                if isinstance(klass, RelatedObject) and klass.field.primary_key and klass.opts == self._meta:
                    self._class = klass.get_accessor_name()
                    break
        return super(Application, self).save(*args, **kwargs)

    def get_object(self):
        try:
            if self._class and self._meta.get_field_by_name(self._class)[0].opts != self._meta:
                return getattr(self, self._class)
        except FieldDoesNotExist:
            pass
        return self


class UserApplication(Application):
    """ Associated with an Applicant or a Person"""
    project = models.ForeignKey(Project, null=True, blank=True, limit_choices_to={'is_active': True})
    needs_account = models.BooleanField(u"Do you require a cluster account?", help_text=u"Will you be working on the project yourself?")
    make_leader = models.BooleanField(help_text="Make this person a project leader")

    @models.permalink
    def get_absolute_url(self):
        return ('kg_userapplication_detail', [self.id])

    def approve(self):
        if self.content_type.model == 'applicant':
            person = self.applicant.approve()
        else:
            person = self.applicant
        if self.needs_account:
            from karaage.projects.utils import add_user_to_project
            add_user_to_project(person, self.project)
        if self.make_leader:
            self.project.leaders.add(person)
        self.state = Application.COMPLETE
        self.save()
        return person
                

class ProjectApplication(Application):
    name = models.CharField('Title', max_length=200)
    institute = models.ForeignKey(Institute, limit_choices_to={'is_active': True})
    description = models.TextField(null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)
    needs_account = models.BooleanField(u"Do you require a cluster account?", help_text=u"Will you be working on the project yourself?")
    machine_categories = models.ManyToManyField(MachineCategory, null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('kg_projectapplication_detail', [self.id])


class Applicant(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=16, unique=True, help_text="Required. 16 characters or fewer. Letters, numbers and underscores only", null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
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
        from karaage.datastores import create_new_person_from_applicant as create_new_person
        person = create_new_person(self)
        person.activate()
        return person
        
