from django.db import models

from andsome.middleware.threadlocals import get_current_user

from karaage.constants import TITLES, COUNTRIES
from karaage.util import new_random_token
from karaage.people.models import Person, Institute
from karaage.projects.models import Project



APPLICATION_STATES = (
    ('N', 'New'),
    ('O', 'Open'),
    ('S', 'Submitted'),
)

class Application(models.Model):
    secret_token = models.CharField(max_length=64, default=new_random_token, editable=False, unique=True)
    created_by = models.ForeignKey(Person, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=1, choices=APPLICATION_STATES, default='N')
    email = models.EmailField()
    username = models.CharField(max_length=16, unique=True, help_text="Required. 16 characters or fewer. Letters, numbers and @.+-_ characters", null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField("Office Telephone", max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)
    supervisor = models.CharField(max_length=100, null=True, blank=True)
    institute = models.ForeignKey(Institute, null=True, blank=True)
    title = models.CharField(choices=TITLES, max_length=10, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    header_message = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = get_current_user().get_profile()
        super(Application, self).save(*args, **kwargs)


class UserApplication(Application):
    project = models.ForeignKey(Project)
    needs_account = models.BooleanField(u"Do you require a cluster account?", help_text=u"Will you be working on the project yourself?")
    make_leader = models.BooleanField(help_text="Make this person a project leader")


