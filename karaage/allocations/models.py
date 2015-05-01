# Copyright 2014 The University of Melbourne
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

from django.db import models

from audit_log.models.managers import AuditLog
from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
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
        app_label = 'karaage'


class AllocationPoolQuerySet(models.QuerySet):
    def with_quantities(self):
        return self.annotate(
            allocated=models.Sum('allocation__quantity'),
            used=models.Sum('usage__used'),
            raw_used=models.Sum('usage__raw_used'),
            # TODO: used_percent=
            # 100 * Sum('allocation__quantity')) / Sum('usage__used')
            # TODO: remaining=
            # Sum('allocation__quantity')) - Sum('usage__used')
        )


@python_2_unicode_compatible
class AllocationPool(models.Model):

    """
    Grouping of resources allocated to a grant (project).

    AllocationMode='capped' is not supported yet, until a demonstratted need is
    shown (and optionally that we can use an array of foreign key to relate
    from Usage to AllocationPool to avoid the M2M join table).

    TODO: User documentation of the allocation behaviour with concrete
    examples.
    """

    project = models.ForeignKey('karaage.Project')
    period = models.ForeignKey('karaage.AllocationPeriod')
    resource_pool = models.ForeignKey('karaage.ResourcePool')

    @cached_property
    def allocated(self):
        return self.allocation_set.aggregate(
            a=models.Sum('quantity'))['a'] or 0.0

    @cached_property
    def used(self):
        return self.usage_set.aggregate(u=models.Sum('used'))['u'] or 0.0

    @cached_property
    def raw_used(self):
        return self.usage_set.aggregate(r=models.Sum('raw_used'))['r'] or 0.0

    @cached_property
    def used_percent(self):
        if self.allocated == 0.0:
            return None
        return 100.0 * self.used / self.allocated

    @cached_property
    def remaining(self):
        return self.allocated - self.used

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
        app_label = 'karaage'
        unique_together = (
            'project',
            'period',
            'resource_pool',
        )


class Allocation(models.Model):
    description = models.CharField(max_length=100)
    grant = models.ForeignKey('karaage.Grant')
    allocation_pool = models.ForeignKey('karaage.AllocationPool')
    quantity = models.FloatField()

    audit_log = AuditLog()

    def __str__(self):
        return self.description

    class Meta:
        ordering = [
            'allocation_pool',
        ]
        app_label = 'karaage'


class AllocationPeriod(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    audit_log = AuditLog()

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            '-end',
            'name',
        ]
        app_label = 'karaage'
