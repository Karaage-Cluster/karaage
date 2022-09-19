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

# Django 1.6 Hack: Ensure tldap.django gets initialised.
import django
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin


if django.VERSION < (1, 7):
    import tldap.django  # NOQA

# threadlocals middleware
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()


def get_current_user():
    return getattr(_thread_locals, "user", None)


def reset():
    _thread_locals.user = None


class ThreadLocals(MiddlewareMixin):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def process_request(self, request):
        # We need to retrieve the actual value of the user here.
        # Otherwise it might be too late when we need it.
        # See commit cf8e22f95894b8922de771ca52946a3966fe6c90.
        user = auth.get_user(request)
        request.user = user
        _thread_locals.user = user
