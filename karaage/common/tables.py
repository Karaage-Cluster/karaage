# Copyright 2014-2015 VPAC
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

import six

import django_tables2 as tables
from django_tables2.utils import A
from django_tables2.columns.linkcolumn import BaseLinkColumn
import django_filters
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from .models import LogEntry


class ObjectColumn(BaseLinkColumn):

    def __init__(self, *args, **kwargs):
        super(ObjectColumn, self).__init__(*args, empty_values=(), **kwargs)

    def render(self, record):
        try:
            obj = record.content_object
        except ContentType.DoesNotExist:
            return "gone: %s" % record.object_repr

        if obj is None:
            return "none: %s" % record.object_repr

        url = obj.get_absolute_url()
        try:
            # django-tables >= 1.2.0
            link = self.render_link(url, record=obj, value=six.text_type(obj))
        except TypeError:
            # django-tables < 1.2.0
            link = self.render_link(url, text=six.text_type(obj))
        return link


class LogEntryFilter(django_filters.FilterSet):
    begin_action_time = django_filters.DateFilter(
        name="action_time", lookup_type="gte")
    end_action_time = django_filters.DateFilter(
        name="action_time", lookup_type="lte")

    class Meta:
        model = LogEntry
        fields = ("begin_action_time", "end_action_time",
                  "content_type", "object_id")


class LogEntryTable(tables.Table):
    user = tables.LinkColumn('kg_person_detail', args=[A('user.username')])
    obj = ObjectColumn(
        verbose_name="Object", order_by=['content_type', 'object_id'])

    def render_action_flag(self, record):
        if record.is_addition():
            html = '<span class="addlink">Add</span>'
        elif record.is_change():
            html = '<span class="changelink">Change</span>'
        elif record.is_deletion():
            html = '<span class="deletelink">Delete</span>'
        elif record.is_comment():
            html = '<span class="commentlink">Comment</span>'
        else:
            html = '-'
        return mark_safe(html)

    class Meta:
        model = LogEntry
        fields = ('action_time', 'user', 'obj', 'action_flag',
                  'change_message')
