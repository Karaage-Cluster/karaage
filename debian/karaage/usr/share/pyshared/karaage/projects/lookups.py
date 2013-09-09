# Copyright 2007-2010 VPAC
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

from django.db.models import Q
from django.utils.html import escape

from karaage.projects.models import Project

from ajax_select import LookupChannel

class ProjectLookup(LookupChannel):

    def get_query(self, q, request):
        """ return a query set.  you also have access to request.user if needed """

        if not request.user.is_staff:
            return Project.objects.none()

        return Project.objects.filter(Q(pid__icontains=q) | Q(name__icontains=q))

    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.pid

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return escape(u"%s" % (obj))

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return escape(u"%s" % (obj))
