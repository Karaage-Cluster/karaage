# coding: utf-8

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
import six
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_tables2.utils import A, AttributeDict

from karaage.people.tables import PeopleColumn

from .models import Project


class ActiveFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        choices = [
            ("", "Unknown"),
            ("deleted", "Deleted"),
            ("yes", "Yes"),
        ]

        super(ActiveFilter, self).__init__(*args, choices=choices, **kwargs)

    def filter(self, qs, value):
        if value == "deleted":
            qs = qs.filter(is_active=False)
        elif value == "yes":
            qs = qs.filter(is_active=True)

        return qs


class ProjectColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super(ProjectColumn, self).__init__(*args, empty_values=(), **kwargs)

    def render_link(self, uri, value, attrs=None):
        attrs = AttributeDict(attrs if attrs is not None else self.attrs.get("a", {}))
        attrs["href"] = uri

        return format_html(
            "<a {attrs}>{text}</a>",
            attrs=attrs.as_html(),
            text=value,
        )

    def render(self, value):
        if value is not None:
            url = reverse("kg_project_detail", args=[value.id])
            link = self.render_link(url, value=six.text_type(value.pid))
            return link
        else:
            return "—"


class ProjectFilter(django_filters.FilterSet):
    pid = django_filters.CharFilter(lookup_expr="icontains", label="PID")
    name = django_filters.CharFilter(lookup_expr="icontains")
    active = ActiveFilter()

    class Meta:
        model = Project
        fields = ("pid", "name", "institute", "is_approved", "active")


class ProjectTable(tables.Table):
    is_active = tables.Column(order_by="-is_active", verbose_name="active")
    pid = tables.LinkColumn("kg_project_detail", args=[A("id")], verbose_name="PID")
    institute = tables.LinkColumn("kg_institute_detail", args=[A("institute__pk")])
    leaders = PeopleColumn(orderable=False)

    def render_is_active(self, record):
        if not record.is_active:
            html = '<span class="no">Deleted</span>'
        elif not record.is_approved:
            html = '<span class="no">Not approved</span>'
        else:
            html = '<span class="yes">Yes</span>'
        return mark_safe(html)

    class Meta:
        model = Project
        fields = ("is_active", "pid", "name", "institute", "leaders", "last_usage")
        empty_text = "No items"
