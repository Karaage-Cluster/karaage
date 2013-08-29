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

""" Application specific tags. """

from django import template
register = template.Library()


@register.inclusion_tag(
        'applications/application_state.html', takes_context = True)
def application_state(context, application):
    """ Render current state of application, verbose. """
    return {
        'auth': context['auth'],
        'application': application,
    }


@register.inclusion_tag(
        'applications/application_actions.html', takes_context = True)
def application_actions(context):
    """ Render actions available. """
    return {
        'auth': context['auth'],
        'actions': context['actions'],
        'extra': "",
    }


@register.tag(name="application_actions_plus")
def do_application_actions_plus(parser, token):
    """ Render actions available with extra text. """
    nodelist = parser.parse(('end_application_actions',))
    parser.delete_first_token()
    return ApplicationActionsPlus(nodelist)

class ApplicationActionsPlus(template.Node):
    """ Node for rendering actions available with extra text. """
    def __init__(self, nodelist):
        super(ApplicationActionsPlus, self).__init__()
        self.nodelist = nodelist

    def render(self, context):
        extra = self.nodelist.render(context)
        nodelist = template.loader.get_template(
                'applications/application_actions.html')
        new_context = template.context.Context({
            'auth': context['auth'],
            'extra': extra,
            'actions': context['actions'],
        })
        output = nodelist.render(new_context)
        return output
