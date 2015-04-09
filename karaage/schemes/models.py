from django.db import models
from django.db.models import Q

from audit_log.models.managers import AuditLog
from django.utils.encoding import python_2_unicode_compatible


class ActiveSchemeManager(models.Manager):
    def get_queryset(self):
        query = super(ActiveSchemeManager, self).get_queryset()
        return query.filter(closed=None)


class DeletedSchemeManager(models.Manager):
    def get_queryset(self):
        query = super(DeletedSchemeManager, self).get_queryset()
        return query.filter(~Q(closed=None))


@python_2_unicode_compatible
class Scheme(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, null=False, blank=True)
    opened = models.DateField()
    closed = models.DateField(null=True, blank=True)

    objects = models.Manager()
    active = ActiveSchemeManager()
    deleted = DeletedSchemeManager()

    audit_log = AuditLog()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        app_label = 'karaage'
