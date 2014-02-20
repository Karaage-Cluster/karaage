# Copyright 2007-2014 VPAC
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

from karaage.machines.forms import ShellForm
from django import template
register = template.Library()

@register.simple_tag
def shell_field(ua):
    sf = ShellForm()
    sf.initial = {'shell': ua.loginShell()}
    return sf['shell']

class RenderAccountAttrNode(template.Node):

    def __init__(self, account, attr_name, how):
        self.account = template.Variable(account)
        self.attr_name = template.Variable(attr_name)
        self.how = template.Variable(how)

    def render(self, context):
        account = self.account.resolve(context)
        attr_name = self.attr_name.resolve(context)
        how = self.how.resolve(context)
        request = context['request']

        template_name = 'machines/account_attr_%s_%s.html' % (attr_name, how)
        template_obj = template.loader.get_template(template_name)

        context = template.RequestContext(request, {
            'account': account,
        })
        output = template_obj.render(context)
        return output

@register.tag
def render_account_attr(parser, token):
    try:
        _, account, attr_name, how = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    return RenderAccountAttrNode(account, attr_name, how)


