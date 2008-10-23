from django.db import models

from karaage.machines.models import MachineCategory
from karaage.people.models import Institute

class InstituteQuota(models.Model):
    institute = models.ForeignKey(Institute)
    machine_category = models.ForeignKey(MachineCategory)
    quota = models.DecimalField(max_digits=5, decimal_places=2)
    cap = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'institute_quota'

    def __unicode__(self):
        return '%s - %s' % (self.institute, self.machine_category)
