# Copyright 2013-2015 VPAC
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

from django.utils.html import escape
from django.core.exceptions import PermissionDenied
from django.db.models import Q

import ajax_select

from karaage.common import is_admin
from karaage.people.models import Person, Group


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


class PersonLookup(LookupChannel):
    model = Person

    def get_query(self, q, request):
        """ return a query set searching for the query string q
            either implement this method yourself or set the search_field
            in the LookupChannel class definition
        """
        return Person.objects.filter(
            Q(username__icontains=q) |
            Q(short_name__icontains=q) |
            Q(full_name__icontains=q)
        )

    def get_result(self, obj):
        """
        result is the simple text that is the completion of what the person
        typed
        """
        return obj.username

    def format_match(self, obj):
        """
        (HTML) formatted item for display in the dropdown
        """
        return "%s (%s)" % (
            escape(obj.full_name),
            escape(obj.username)
        )

    def format_item_display(self, obj):
        """
        (HTML) formatted item for displaying item in the selected deck area
        """
        return "%s" % (
            escape(obj.full_name)
        )


class GroupLookup(LookupChannel):
    model = Group

    def get_query(self, q, request):
        """ return a query set searching for the query string q
            either implement this method yourself or set the search_field
            in the LookupChannel class definition
        """
        return Group.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    def get_result(self, obj):
        """
        result is the simple text that is the completion of what the person
        typed
        """
        return obj.name

    def format_match(self, obj):
        """
        (HTML) formatted item for display in the dropdown
        """
        result = [escape(obj.name)]

        if obj.description:
            result.append(escape(obj.description))

        return " ".join(result)

    def format_item_display(self, obj):
        """
        (HTML) formatted item for displaying item in the selected deck area
        """
        return "%s" % (
            escape(obj.name)
        )
