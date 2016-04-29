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

# Django 1.6 Hack: Ensure tldap.django gets initialised.
import django
if django.VERSION < (1, 7):
    import tldap.django  # NOQA

# threadlocals middleware
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def reset():
    _thread_locals.user = None


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
