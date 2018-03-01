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

import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import A

from .models import Account, Machine


class MachineTable(tables.Table):
    name = tables.LinkColumn(
        'kg_machine_detail', args=[A('pk')])
    status = tables.Column(
        empty_values=(), order_by=('end_date', 'start_date'))

    def render_status(self, record):
        if record.end_date is not None:
            return "Decommissioned %s" % record.end_date
        else:
            return "Active since %s" % record.start_date

    class Meta:
        model = Machine
        fields = ("name", )
        empty_text = "No items"


class AccountTable(tables.Table):
    active = tables.Column(
        empty_values=(), order_by=('date_deleted', '-login_enabled'))
    person = tables.LinkColumn(
        'kg_person_detail', args=[A('person.username')])
    username = tables.LinkColumn(
        'kg_account_detail', args=[A('pk')], verbose_name="Account")
    default_project = tables.LinkColumn(
        'kg_project_detail', args=[A('default_project.id')])

    def render_active(self, record):
        if record.date_deleted is not None:
            html = '<span class="no">Deleted</span>'
        elif not record.login_enabled:
            html = '<span class="locked">Locked</span>'
        else:
            html = '<span class="yes">Yes</span>'
        return mark_safe(html)

    class Meta:
        model = Account
        fields = ("active", "username", "person",
                  "default_project", "date_created", "date_deleted")
