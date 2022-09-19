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

import django_filters
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A

from .models import LogEntry


class LogEntryFilter(django_filters.FilterSet):
    begin_action_time = django_filters.DateFilter(field_name="action_time", lookup_expr="gte")
    end_action_time = django_filters.DateFilter(field_name="action_time", lookup_expr="lte")

    class Meta:
        model = LogEntry
        fields = ("begin_action_time", "end_action_time", "content_type", "object_id")


class LogEntryTable(tables.Table):
    user = tables.LinkColumn("kg_person_detail", args=[A("user__username")])
    content_object = tables.Column(linkify=True, verbose_name="Object", order_by=["content_type", "object_id"])

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
            html = "-"
        return mark_safe(html)

    class Meta:
        model = LogEntry
        fields = ("action_time", "user", "obj", "action_flag", "change_message")
        empty_text = "No items"
