# Copyright 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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

from __future__ import unicode_literals
from __future__ import absolute_import

import six

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.encoding import smart_text
from django.utils.encoding import python_2_unicode_compatible

from karaage.middleware.threadlocals import get_current_user

ADDITION = 1
CHANGE = 2
DELETION = 3
COMMENT = 4


@python_2_unicode_compatible
class Usage(models.Model):
    account = models.ForeignKey('karaage.Account')
    allocation_pool = models.ForeignKey('karaage.AllocationPool', null=True)
    allocation_period = models.ForeignKey(
        'karaage.AllocationPeriod', null=True)
    content_type = models.ForeignKey('contenttypes.ContentType')
    grant = models.ForeignKey('karaage.Grant', null=True)
    person_institute = models.ForeignKey(
        'karaage.Institute',
        related_name='person_institute',
        null=True,
    )
    project_institute = models.ForeignKey(
        'karaage.Institute',
        related_name='project_institute',
    )
    machine = models.ForeignKey('karaage.Machine')
    person = models.ForeignKey('karaage.Person', null=True)
    submitted_project = models.ForeignKey(
        'karaage.Project',
        related_name='submitted_usage',
    )
    allocated_project = models.ForeignKey(
        'karaage.Project',
        related_name='allocated_usage',
        null=True,
    )
    resource = models.ForeignKey('karaage.Resource')
    resource_pool = models.ForeignKey('karaage.ResourcePool', null=True)
    scheme = models.ForeignKey('karaage.Scheme', null=True)
    person_project_level = models.ForeignKey(
        'karaage.ProjectLevel',
        blank=True, null=True,  # legacy data doesn't have person project level
    )
    person_career_level = models.ForeignKey(
        'karaage.CareerLevel',
        blank=True, null=True,  # legacy data doesn't have person career level
    )
    count = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    range_start = models.DateTimeField()
    range_end = models.DateTimeField()
    raw_used = models.FloatField()
    used = models.FloatField()

    def __str__(self):
        return self.description

    class Meta:
        # Not using ordering so database planner is free to pick the
        # rows as they come.
        pass


class LogEntryManager(models.Manager):

    def log_action(self, user_id, content_type_id, object_id,
                   object_repr, action_flag, change_message=''):
        msg = self.model(None, None, user_id, content_type_id, object_id,
                         object_repr[:200], action_flag, change_message)
        msg.save()
        return msg

    def log_object(self, obj, flag, message, user=None):
        assert obj is not None
        assert obj.pk is not None
        if user is None:
            user = get_current_user()
        if user is None:
            user_id = None
        else:
            user_id = user.pk
        return self.log_action(
            user_id=user_id,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=six.text_type(obj),
            action_flag=flag,
            change_message=message)


@python_2_unicode_compatible
class LogEntry(models.Model):
    action_time = models.DateTimeField(_('action time'), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField(_('object id'), blank=True, null=True)
    content_object = generic.GenericForeignKey(ct_field="content_type",
                                               fk_field="object_id")
    object_repr = models.CharField(_('object repr'), max_length=200)
    action_flag = models.PositiveSmallIntegerField(_('action flag'))
    change_message = models.TextField(_('change message'), blank=True)

    objects = LogEntryManager()

    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        db_table = 'admin_log'
        app_label = 'karaage'
        ordering = ('-action_time', '-pk')

    def __repr__(self):
        return smart_text(self.action_time)

    def __str__(self):
        if self.action_flag == ADDITION:
            return ugettext('Added "%(object)s".') % \
                {'object': self.object_repr}
        elif self.action_flag == CHANGE:
            return ugettext('Changed "%(object)s" - %(changes)s') % {
                'object': self.object_repr,
                'changes': self.change_message,
            }
        elif self.action_flag == DELETION:
            return ugettext('Deleted "%(object)s."') % \
                {'object': self.object_repr}
        elif self.action_flag == COMMENT:
            return ugettext('Comment "%(object)s" - %(changes)s') % {
                'object': self.object_repr,
                'changes': self.change_message,
            }

        return ugettext('LogEntry Object')

    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION

    def is_comment(self):
        return self.action_flag == COMMENT
