from django.db import models

from audit_log.models.managers import AuditLog


class Grant(models.Model):
    project = models.ForeignKey('karaage.Project')
    scheme = models.ForeignKey('karaage.Scheme')
    description = models.CharField(max_length=255)
    date = models.DateField()
    begins = models.DateField()
    expires = models.DateField()

    audit_log = AuditLog()

    class Meta:
        ordering = [
            '-expires',
            '-project__end_date',
            'project__name',
            'description',
        ]


class AllocationPool(models.Model):
    grant = models.ForeignKey('karaage.Grant')
    period = models.ForeignKey('karaage.AllocationPeriod')
    resource_pool = models.ForeignKey('karaage.ResourcePool')

    audit_log = AuditLog()

    class Meta:
        ordering = [
            '-period__end',
            '-grant__expires',
            '-grant__project__end_date',
            'grant__project__name',
        ]


class Allocation(models.Model):
    allocation_pool = models.ForeignKey('karaage.AllocationPool')
    quantity = models.FloatField()

    audit_log = AuditLog()

    class Meta:
        ordering = [
            'allocation_pool',
        ]


class AllocationPeriod(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()

    audit_log = AuditLog()

    class Meta:
        ordering = [
            '-end',
            'name',
        ]
