# Copyright 2007-2014 VPAC
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
from django_tables2.columns.linkcolumn import BaseLinkColumn
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class PeopleColumn(BaseLinkColumn):
    def render(self, value):
        people = []
        for person in value.all():
            url = reverse("kg_person_detail", args=[person.username])
            link = self.render_link(url, text=unicode(person))
            people.append(link)
        return mark_safe(", ".join(people))
