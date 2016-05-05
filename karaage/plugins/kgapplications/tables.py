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

import six

import django_tables2 as tables
from django_tables2.utils import A
from django_tables2.columns.linkcolumn import BaseLinkColumn
import django_filters

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from karaage.people.models import Person

from .models import Application
from .views.base import get_state_machine


class ApplicantColumn(BaseLinkColumn):

    def render(self, value):
        if isinstance(value, Person):
            url = reverse("kg_person_detail", args=[value.username])
            try:
                # django-tables >= 1.2.0
                link = self.render_link(
                    url, record=value, value=six.text_type(value))
            except TypeError:
                # django-tables < 1.2.0
                link = self.render_link(url, text=six.text_type(value))
            return mark_safe(link)
        else:
            return value.email


class ApplicationFilter(django_filters.FilterSet):

    class Meta:
        model = Application
        fields = ('secret_token',)


class ApplicationTable(tables.Table):
    id = tables.LinkColumn(
        'kg_application_detail', args=[A('pk')], verbose_name="ID")
    action = tables.Column(
        empty_values=(), order_by=('date_deleted', '-login_enabled'))
    applicant = ApplicantColumn()

    def render_action(self, record):
        return record.get_object().info()

    def render_state(self, record):
        state_machine = get_state_machine(record)
        state = state_machine.get_state(record)
        return state.name

    class Meta:
        model = Application
        fields = ('id', 'action', 'applicant', 'state', 'expires')
