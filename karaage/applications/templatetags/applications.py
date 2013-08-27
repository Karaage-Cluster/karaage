# Copyright 2013 VPAC
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

from django.template import Library
register = Library()

import karaage.applications.models as models

def application_state(context, application):
    return {
        'auth': context['auth'],
        'application': application,
    }
register.inclusion_tag('applications/application_state.html', takes_context=True)(application_state)


def application_actions(context):
    return {
        'auth': context['auth'],
        'actions': context['actions'],
    }
register.inclusion_tag('applications/application_actions.html', takes_context=True)(application_actions)


@register.filter
def is_userapplication(application):
    return isinstance(application, models.UserApplication)

@register.filter
def is_projectapplication(application):
    return isinstance(application, models.ProjectApplication)
