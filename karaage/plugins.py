# Copyright 2014-2015 VPAC
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

import django
if django.VERSION < (1, 7):
    parent = object
else:
    from django.apps import AppConfig
    parent = AppConfig


class BasePlugin(parent):
    name = None
    django_apps = ()
    depends = ()
    xmlrpc_methods = ()
    settings = {}
    template_context_processors = ()
