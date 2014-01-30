# Copyright 2007-2013 VPAC
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

from django.template import Library
from django.conf import settings
from django import template
from django.template import resolve_variable, RequestContext

register = Library()

@register.simple_tag(takes_context=True)
def inline_render(context, renderable):
    if not renderable:
        return ''
    template, ctx = renderable
    return template.render(RequestContext(context['request'],
                                          ctx))
