from django.db import models
from django.db.models.signals import post_save, pre_delete

from decimal import Decimal
import datetime

from karaage.people.models import Institute
from karaage.projects.models import Project
from karaage.machines.models import MachineCategory


class InstituteChunk(models.Model):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    quota = models.DecimalField(max_digits=5, decimal_places=2)
    cap = models.IntegerField(null=True, blank=True)
    disk_quota = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'institute_quota'
        unique_together = ('institute', 'machine_category')

    def __unicode__(self):
        return '%s - %s' % (self.institute, self.machine_category)

    def get_absolute_url(self):
        return self.institute.get_absolute_url()

    def get_cap(self):
        if self.cap:
            return self.cap
        if self.quota:
            return self.quota * 1000
        return None



class ProjectChunk(models.Model):
    project = models.ForeignKeyField(Project)
    cap = models.IntegerField(null=True, blank=True)
    machine_category = models.ForeignKey(MachineCategory)

    def get_mpots(self, start=datetime.date.today()-datetime.timedelta(days=90), end=datetime.date.today()):
	from karaage.util.helpers import get_available_time

        TWOPLACES = Decimal(10) ** -2
        usage, jobs = self.project.get_usage(start, end)
        if usage is None:
            usage = Decimal('0')
        total_time, ave_cpus = get_available_time()
        
        return ((usage / total_time) * 100 * 1000).quantize(TWOPLACES)

    def is_over_quota(self):
        if self.get_mpots() > self.get_cap():
            return True
        return False

    def get_cap(self):
        try:
            iq = self.project.institute.institutechunk_set.get(machine_category=self.machine_category)
        except:
            print 'failed'
            return None

        if self.cap is not None:
            return self.cap
        if iq.cap is not None:
            return iq.cap
        return iq.quota * 1000



def create_project_chunk(sender, **kwargs):
    project = kwargs['instance']
    for mc in project.machine_categories.all():
        ProjectChunk.objects.get_or_create(project=project, machine_category=mc)

def delete_project_chunk(sender, **kwargs):
    ProjectChunk.objects.filter(project=kwargs['instance']).delete()



post_save.connect(create_project_chunk, sender=Project)
pre_delete.connect(delete_project_chunk, sender=Project)
