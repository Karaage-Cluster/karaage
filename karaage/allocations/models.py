from django.db import models

from audit_log.models.managers import AuditLog
from django.utils.functional import cached_property

class Grant(models.Model):
    project = models.ForeignKey('karaage.Project')
    scheme = models.ForeignKey('karaage.Scheme')
    description = models.CharField(max_length=255)
    date = models.DateField()
    begins = models.DateField()
    expires = models.DateField()

    audit_log = AuditLog()

    def __str__(self):
        return self.description

    class Meta:
        ordering = [
            '-expires',
            '-project__end_date',
            'project__name',
            'description',
        ]


class AllocationPoolQuerySet(models.QuerySet):
    def with_quantities(self):
        return self.annotate(
            allocated=models.Sum('allocation__quantity'),
            used=models.Sum('usage__used'),
            raw_used=models.Sum('usage__raw_used'),
            # TODO: used_percent= \
            # 100 * Sum('allocation__quantity')) / Sum('usage__used')
        )


class AllocationPool(models.Model):

    """
    Grouping of resources allocated to a grant (project).

    AllocationMode='capped' is not supported yet, until a demonstratted need is
    shown (and optionally that we can use an array of foreign key to relate from
    Usage to AllocationPool to avoid the M2M join table).

    TODO: User documentation of the allocation behaviour with concrete examples.
    """

    project = models.ForeignKey('karaage.Project')
    period = models.ForeignKey('karaage.AllocationPeriod')
    resource_pool = models.ForeignKey('karaage.ResourcePool')

    @cached_property
    def allocated(self):
        return self.allocations_set.aggregate(a=models.Sum('allocated'))['a']
    @cached_property
    def used(self):
        return self.usage_set.aggregate(u=models.Sum('used'))['u']
    @cached_property
    def raw_used(self):
        return self.usage_set.aggregate(r=models.Sum('raw_used'))['r']
    @cached_property
    def used_percent(self):
        return 100.0 * self.used / self.allocated

    objects = AllocationPoolQuerySet.as_manager()
    audit_log = AuditLog()

    def __str__(self):
        return 'Project: %s' % self.project.name

    class Meta:
        ordering = [
            '-period__end',
            '-project__end_date',
            'project__name',
        ]


class Allocation(models.Model):
    description = models.CharField(max_length=100)
    grant = models.ForeignKey('karaage.Grant')
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
