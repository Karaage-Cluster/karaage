# Copyright 2007-2013 VPAC
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

from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

COMMENT_MAX_LENGTH = 3000


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType,
            verbose_name=_('content type'),
            related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    comment = models.TextField(_('comment'), max_length=COMMENT_MAX_LENGTH)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_comments")
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)


    class Meta:
        db_table = "comments"
        ordering = ('submit_date',)
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = timezone.now()
        super(Comment, self).save(*args, **kwargs)

