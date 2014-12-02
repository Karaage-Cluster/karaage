from django.db import models

from audit_log.models.managers import AuditLog

from projects.models import Project
from resources.models import ResourcePool
from schemes.models import Scheme


class Allocation(models.Model):
    grant = models.ForeignKey(Grant)
    period = models.ForeignKey(AllocationPeriod)
    project = models.ForeignKey(Project)
    resource_pool = models.ForeignKey(ResourcePool)
    quantity = models.FloatField()

    audit_log = AuditLog()


class AllocationPeriod(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()

    audit_log = AuditLog()


class Grant(models.Model):
    project = models.ForeignKey(Project)
    scheme = models.ForeignKey(Scheme)
    description = models.CharField(max_length=255)
    date = models.DateField()
    begins = models.DateField()
    expires = models.DateField()

    audit_log = AuditLog()
