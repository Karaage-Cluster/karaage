# Copyright 2010-2015 VPAC
# Copyright 2010 The University of Melbourne
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

from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.html import escape

from karaage.common import is_admin
from karaage.projects.models import Project

import ajax_select


class LookupChannel(ajax_select.LookupChannel):
    """ Base clase for lookups. """

    def check_auth(self, request):
        """
        to ensure that nobody can get your data via json simply by knowing the
        URL.  public facing forms should write a custom LookupChannel to
        implement as you wish.  also you could choose to return
        HttpResponseForbidden("who are you?") instead of raising
        PermissionDenied (401 response)
        """
        if not request.user.is_authenticated():
            raise PermissionDenied
        if not is_admin(request):
            raise PermissionDenied


class ProjectLookup(LookupChannel):
    model = Project

    def get_query(self, q, request):
        """ return a query set searching for the query string q
            either implement this method yourself or set the search_field
            in the LookupChannel class definition
        """
        return Project.objects.filter(
            Q(pid__icontains=q) |
            Q(name__icontains=q)
        )

    def get_result(self, obj):
        """
        result is the simple text that is the completion of what the person
        typed
        """
        return obj.pid

    def format_match(self, obj):
        """
        (HTML) formatted item for display in the dropdown
        """
        return escape(six.u("%s") % obj)

    def format_item_display(self, obj):
        """
        (HTML) formatted item for displaying item in the selected deck area
        """
        return escape(six.u("%s") % obj)
