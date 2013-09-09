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

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(function=None):
    """
    Decorator for views that checks that the user is an administrator,
    redirecting to the log-in page if necessary.
    """
    def check_perms(user):
        # if user not logged in, show login form
        if not user.is_authenticated():
            return False
        # First check if the user has the permission (even anon users)
        if user.is_admin:
            return True
        raise PermissionDenied

    actual_decorator = user_passes_test(
        check_perms,
        login_url="login",
        redirect_field_name="next"
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def login_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url="login",
        redirect_field_name="next"
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
