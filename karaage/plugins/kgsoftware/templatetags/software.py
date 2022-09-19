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

""" Application specific tags. """

import django_tables2 as tables
from django import template

from ..tables import SoftwareLicenseAgreementTable


register = template.Library()


@register.simple_tag(takes_context=True)
def get_software_license_agreement_table(context, queryset):
    table = SoftwareLicenseAgreementTable(queryset)
    config = tables.RequestConfig(context["request"], paginate={"per_page": 5})
    config.configure(table)
    return table
