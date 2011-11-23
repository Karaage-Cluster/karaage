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


class ProjectLookup(object):

    def get_query(self, q, request):
        """ return a query set.  you also have access to request.user if needed """

        if not request.user.is_staff:
            return Project.objects.none()

        return Project.objects.filter(Q(pid__icontains=q) | Q(name__icontains=q))

    def format_result(self, p):
        """ the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """
        return escape(u"%s" % (p))

    def format_item(self, p):
        """ the display of a currently selected object in the area below the search box. html is OK """
        return escape(u"%s" % (p))

    def get_objects(self, ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Project.objects.filter(pk__in=ids)
