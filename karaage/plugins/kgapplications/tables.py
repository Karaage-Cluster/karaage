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
from django_tables2.utils import A

from .models import Application
from .views.base import get_state_machine


class ApplicationFilter(django_filters.FilterSet):
    class Meta:
        model = Application
        fields = ("secret_token",)


class ApplicationTable(tables.Table):
    id = tables.LinkColumn("kg_application_detail", args=[A("pk")], verbose_name="ID")
    action = tables.Column(empty_values=(), order_by=("_class"))
    applicant = tables.Column(linkify=True, order_by=("new_applicant", "existing_person"))

    def render_action(self, record):
        return record.get_object().info()

    def render_state(self, record):
        state_machine = get_state_machine(record)
        state = state_machine.get_state(record)
        return state.name

    class Meta:
        model = Application
        fields = ("id", "action", "applicant", "state", "expires")
        empty_text = "No items"
