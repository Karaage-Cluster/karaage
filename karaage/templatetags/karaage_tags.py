# Copyright 2012 VPAC
#
# This file is part of django-placard.
#
# django-placard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-placard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-placard  If not, see <http://www.gnu.org/licenses/>.


from django.http import QueryDict
from django import template

register = template.Library()

class url_with_param_node(template.Node):
    def __init__(self, copy, nopage, changes):
        self.copy = copy
        self.nopage = nopage
        self.changes = []
        for key, newvalue in changes:
            newvalue = template.Variable(newvalue)
            self.changes.append((key, newvalue,))

    def render(self, context):
        if 'request' not in context:
            return ""

        request = context['request']

        result = {}

        if self.copy:
            result = request.GET.copy()
        else:
            result = QueryDict("", mutable=True)

        if self.nopage:
            result.pop("page", None)

        for key, newvalue in self.changes:
            newvalue = newvalue.resolve(context)
            result[key] = newvalue

        return "?" + result.urlencode()


@register.tag
def url_with_param(parser, token):
    bits = token.split_contents()
    qschanges = []

    bits.pop(0)

    copy = False
    if bits[0] == "copy":
        copy = True
        bits.pop(0)

    nopage = False
    if bits[0] == "nopage":
        nopage = True
        bits.pop(0)

    for i in bits:
        try:
            key, newvalue = i.split('=', 1)
            qschanges.append((key, newvalue,))
        except ValueError:
            raise template.TemplateSyntaxError, "Argument syntax wrong: should be key=value"
    return url_with_param_node(copy, nopage, qschanges)
