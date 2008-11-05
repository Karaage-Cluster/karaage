from django.db import models

import datetime
from decimal import Decimal

from karaage.people.models import Person, Institute
from karaage.machines.models import MachineCategory

from managers import ActiveProjectManager, DeletedProjectManager


class Project(models.Model):
    pid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(Person, blank=True, null=True)
    institute = models.ForeignKey(Institute)
    leader = models.ForeignKey(Person, related_name='leader')
    description = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_expertise = models.BooleanField()
    additional_req = models.TextField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)
    is_active = models.BooleanField()
    approved_by = models.ForeignKey(Person, related_name='project_approver', null=True, blank=True, editable=False)
    date_approved = models.DateField(null=True, blank=True, editable=False)
    deleted_by = models.ForeignKey(Person, related_name='project_deletor', null=True, blank=True, editable=False)
    date_deleted = models.DateField(null=True, blank=True, editable=False)
    last_usage = models.DateField(null=True, blank=True, editable=False)
    cap = models.IntegerField(null=True, blank=True)
    objects = models.Manager()
    active = ActiveProjectManager()
    deleted = DeletedProjectManager()

    class Meta:
        ordering = ['institute', 'pid']
        db_table = 'project'

    def __unicode__(self):
        return '%s - %s' % (self.pid, self.name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('kg_project_detail', [self.pid])
        
    @models.permalink
    def get_usage_url(self):
        return ('kg_project_usage', [self.institute.id, self.pid])
        
    def deactivate(self):
        self.is_active = False
        deletor = get_current_user()    
        self.deleted_by = deletor.get_profile()
        self.date_deleted = datetime.datetime.today()
        self.users.clear()
        self.save()

    def get_usage(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):
        from karaage.util.usage import get_project_usage
        return get_project_usage(self, start, end)

    def gen_usage_graph(self, start, end, machine_category=None):
        if machine_category is None:
            machine_category = self.machine_category
        from karaage.graphs import gen_project_graph
        gen_project_graph(self, start, end, machine_category)

    def get_latest_usage(self):
        return self.cpujob_set.all()[:5]

    def get_cap(self):
        try:
            iq = self.institute.institutequota_set.filter(machine_category=self.machine_category)[0]
        except:
            return None

        if self.cap is not None:
            return self.cap
        if iq.cap is not None:
            return iq.cap
        return iq.quota * 1000


    def get_mpots(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):

        TWOPLACES = Decimal(10) ** -2
        from karaage.util.helpers import get_available_time
        usage, jobs = self.get_usage(start, end)
        if usage is None:
            usage = Decimal('0')
        total_time, ave_cpus = get_available_time()
        
        return ((usage / total_time) * 100 * 1000).quantize(TWOPLACES)

    def is_over_quota(self):
        if self.get_mpots() > self.get_cap():
            return True
        return False
