# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

from __future__ import absolute_import, unicode_literals

import six
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from karaage.middleware.threadlocals import get_current_user


ADDITION = 1
CHANGE = 2
DELETION = 3
COMMENT = 4


class LogEntryManager(models.Manager):
    def log_action(self, user_id, content_type_id, object_id, object_repr, action_flag, change_message=""):
        msg = self.model(
            None, None, user_id, content_type_id, object_id, object_repr[:200], action_flag, change_message
        )
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
            change_message=message,
        )


class LogEntry(models.Model):
    action_time = models.DateTimeField(_("action time"), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.TextField(_("object id"), blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField(_("object repr"), max_length=200)
    action_flag = models.PositiveSmallIntegerField(_("action flag"))
    change_message = models.TextField(_("change message"), blank=True)

    objects = LogEntryManager()

    class Meta:
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")
        db_table = "admin_log"
        app_label = "karaage"
        ordering = ("-action_time", "-pk")

    def __repr__(self):
        return smart_str(self.action_time)

    def __str__(self):
        if self.action_flag == ADDITION:
            return gettext('Added "%(object)s".') % {"object": self.object_repr}
        elif self.action_flag == CHANGE:
            return gettext('Changed "%(object)s" - %(changes)s') % {
                "object": self.object_repr,
                "changes": self.change_message,
            }
        elif self.action_flag == DELETION:
            return gettext('Deleted "%(object)s."') % {"object": self.object_repr}
        elif self.action_flag == COMMENT:
            return gettext('Comment "%(object)s" - %(changes)s') % {
                "object": self.object_repr,
                "changes": self.change_message,
            }

        return gettext("LogEntry Object")

    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION

    def is_comment(self):
        return self.action_flag == COMMENT
