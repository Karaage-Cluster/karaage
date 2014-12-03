from django.db import models

from audit_log.models.managers import AuditLog


class Allocation(models.Model):
    grant = models.ForeignKey('karaage.Grant')
    period = models.ForeignKey('karaage.AllocationPeriod')
    project = models.ForeignKey('karaage.Project')
    resource_pool = models.ForeignKey('karaage.ResourcePool')
    quantity = models.FloatField()

    audit_log = AuditLog()


class AllocationPeriod(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()

    audit_log = AuditLog()


class Grant(models.Model):
    project = models.ForeignKey('karaage.Project')
    scheme = models.ForeignKey('karaage.Scheme')
    description = models.CharField(max_length=255)
    date = models.DateField()
    begins = models.DateField()
    expires = models.DateField()

    audit_log = AuditLog()
