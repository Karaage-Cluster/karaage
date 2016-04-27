# Copyright 2015 VPAC
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

import django_tables2 as tables

from django import template

from karaage.people.tables import PersonTable

from ..views.base import get_state_machine

register = template.Library()


@register.simple_tag(takes_context=True)
def application_state(context, application):
    """ Render current state of application, verbose. """
    new_context = template.context.Context({
        'roles': context['roles'],
        'org_name': context['org_name'],
        'application': application,
    })
    nodelist = template.loader.get_template(
        'kgapplications/%s_common_state.html' % application.type)
    output = nodelist.render(new_context)
    return output


@register.simple_tag(takes_context=True)
def application_request(context, application):
    """ Render current detail of application, verbose. """
    new_context = template.context.Context({
        'roles': context['roles'],
        'org_name': context['org_name'],
        'application': application,
    })
    nodelist = template.loader.get_template(
        'kgapplications/%s_common_request.html' % application.type)
    output = nodelist.render(new_context)
    return output


@register.simple_tag(takes_context=True)
def application_simple_state(context, application):
    """ Render current state of application, verbose. """
    state_machine = get_state_machine(application)
    state = state_machine.get_state(application)
    return state.name


@register.inclusion_tag(
    'kgapplications/common_actions.html', takes_context=True)
def application_actions(context):
    """ Render actions available. """
    return {
        'roles': context['roles'],
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
            'kgapplications/common_actions.html')
        new_context = template.context.Context({
            'roles': context['roles'],
            'extra': extra,
            'actions': context['actions'],
        })
        output = nodelist.render(new_context)
        return output


@register.assignment_tag(takes_context=True)
def get_similar_people_table(context, applicant):
    queryset = applicant.similar_people()
    table = PersonTable(queryset)
    config = tables.RequestConfig(context['request'], paginate={"per_page": 5})
    config.configure(table)
    return table
