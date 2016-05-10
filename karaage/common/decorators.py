# Copyright 2013-2015 VPAC
# Copyright 2014 The University of Melbourne
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

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


if settings.SHIB_SUPPORTED:
    _login_url = "kg_profile_login_saml"
else:
    _login_url = "kg_profile_login"


def admin_required(function=None):
    """
    Decorator for views that checks that the user is an administrator,
    redirecting to the log-in page if necessary.
    """
    def check_perms(user):
        # if user not logged in, show login form
        if not user.is_authenticated():
            return False
        # if this site doesn't allow admin access, fail
        if settings.ADMIN_IGNORED:
            raise PermissionDenied
        # check if the user has admin rights
        if not user.is_admin:
            raise PermissionDenied
        return True

    actual_decorator = user_passes_test(check_perms, login_url=_login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator


def login_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def check_perms(user):
        # if user not logged in, show login form
        if not user.is_authenticated():
            return False
        # if this is the admin site only admin access
        if settings.ADMIN_REQUIRED and not user.is_admin:
            raise PermissionDenied
        return True

    actual_decorator = user_passes_test(check_perms, login_url=_login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator


def usage_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def check_perms(user):
        # if user not logged in, show login form
        if not user.is_authenticated():
            return False
        # if this is the admin site only admin access
        if settings.ADMIN_REQUIRED and not user.is_admin:
            raise PermissionDenied
        if settings.USAGE_IS_PUBLIC:
            return True
        if user.is_admin:
            return True
        return False

    actual_decorator = user_passes_test(check_perms, login_url=_login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator


def xmlrpc_machine_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def actual_decorator(func):
        def wrapper(machine_name, password, *args):
            from django_xmlrpc.decorators import AuthenticationFailedException
            from karaage.machines.models import Machine
            machine = Machine.objects.authenticate(machine_name, password)
            if machine is None:
                raise AuthenticationFailedException
            return func(machine, *args)

        if hasattr(func, '_xmlrpc_signature'):
            sig = func._xmlrpc_signature
            sig['args'] = (['string'] * 2) + sig['args']
            wrapper._xmlrpc_signature = sig

        if func.__doc__:
            wrapper.__doc__ = func.__doc__ + \
                "\nNote: Machine authentication is required."
        return wrapper

    if function:
        return actual_decorator(function)
    return actual_decorator
