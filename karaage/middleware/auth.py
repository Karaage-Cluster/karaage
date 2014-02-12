# Copyright 2007-2013 VPAC
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

from django.contrib.auth import login
from django.http import HttpResponseForbidden

from karaage.people.models import Person

class ApacheSiteLogin:
    "This middleware logs a user in using the REMOTE_USER header from apache"
    def process_request(self, request):

        if request.user.is_anonymous():
            try:
                person = Person.objects.get(username__exact=request.META['REMOTE_USER'])
                login(request, person)
            except:
                return HttpResponseForbidden("<h1>Failed log in.</h1><p>Try to refresh page</p>")
