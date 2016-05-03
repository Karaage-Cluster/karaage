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
from django_tables2.columns.linkcolumn import BaseLinkColumn
from django_tables2.utils import A

import django_filters

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import Person, Group


class ActiveFilter(django_filters.ChoiceFilter):

    def __init__(self, *args, **kwargs):
        choices = [
            ('', 'Unknown'),
            ('deleted', 'Deleted'),
            ('locked', 'Locked'),
            ('yes', 'Yes'),
        ]

        super(ActiveFilter, self).__init__(*args, choices=choices, **kwargs)

    def filter(self, qs, value):
        if value == "deleted":
            qs = qs.filter(date_deleted__isnull=False)
        elif value == "locked":
            qs = qs.filter(date_deleted__isnull=True, login_enabled=False)
        elif value == "yes":
            qs = qs.filter(date_deleted__isnull=True, login_enabled=True)

        return qs


class PeopleColumn(BaseLinkColumn):

    def render(self, value):
        people = []
        for person in value.all():
            url = reverse("kg_person_detail", args=[person.username])
            try:
                # django-tables >= 1.2.0
                link = self.render_link(
                    url, record=person, value=six.text_type(person))
            except TypeError:
                # django-tables < 1.2.0
                link = self.render_link(url, text=six.text_type(person))
            people.append(link)
        return mark_safe(", ".join(people))


class PersonFilter(django_filters.FilterSet):
    active = ActiveFilter()
    username = django_filters.CharFilter(lookup_type="icontains")
    full_name = django_filters.CharFilter(lookup_type="icontains")
    email = django_filters.CharFilter(lookup_type="icontains")
    no_last_usage = django_filters.BooleanFilter(
        name="last_usage", lookup_expr="isnull")
    begin_last_usage = django_filters.DateFilter(
        name="last_usage", lookup_type="gte")
    end_last_usage = django_filters.DateFilter(
        name="last_usage", lookup_type="lte")
    begin_date_approved = django_filters.DateFilter(
        name="date_approved", lookup_type="gte")
    end_date_approved = django_filters.DateFilter(
        name="date_approved", lookup_type="lte")

    class Meta:
        model = Person
        fields = ("active", "username", "full_name", "email", "institute",
                  "is_admin", )


class PersonTable(tables.Table):
    active = tables.Column(
        empty_values=(), order_by=('date_deleted', '-login_enabled'))
    username = tables.LinkColumn(
        'kg_person_detail', args=[A('username')])
    institute = tables.LinkColumn(
        'kg_institute_detail', args=[A('institute.pk')])

    def render_active(self, record):
        if record.date_deleted is not None:
            html = '<span class="no">Deleted</span>'
        elif not record.login_enabled:
            html = '<span class="locked">Locked</span>'
        else:
            html = '<span class="yes">Yes</span>'
        return mark_safe(html)

    class Meta:
        model = Person
        fields = ("active", "username", "full_name", "institute",
                  "is_admin", "last_usage", "date_approved")


class LeaderTable(tables.Table):
    leader = tables.LinkColumn(
        'kg_person_detail', args=[A('leader.username')])
    institute = tables.LinkColumn(
        'kg_institute_detail',
        args=[A('leader.institute.pk')],
        accessor="leader.institute")
    project = tables.LinkColumn(
        'kg_project_detail', args=[A('project.pk')])

    class Meta:
        fields = ("leader", "institute", "project", )


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type="icontains")
    description = django_filters.CharFilter(lookup_type="icontains")

    class Meta:
        model = Group
        fields = ("name", "description")


class GroupTable(tables.Table):
    name = tables.LinkColumn(
        'kg_group_detail', args=[A('name')])
    members = PeopleColumn(orderable=False)

    class Meta:
        model = Group
        fields = ("name", "description")
