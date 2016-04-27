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

import six

from django.template import Library
from django import template

register = Library()


@register.inclusion_tag('karaage/common/inlineformfield.html')
def inlineformfield(field1, field2, field3=False):
    return locals()


@register.inclusion_tag('karaage/common/form_as_div.html')
def form_as_div(form):
    return {'form': form, }


@register.tag
def formfield(parser, token):
    try:
        tag_name, field = token.split_contents()
    except:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly one argument" % token.contents.split()[0])
    return FormFieldNode(field)


class FormFieldNode(template.Node):

    def __init__(self, field):
        self.field = template.Variable(field)

    def get_template(self, class_name):
        try:
            template_name = 'formfield/%s.html' % class_name
            return template.loader.get_template(template_name)
        except template.TemplateDoesNotExist:
            return template.loader.get_template('formfield/default.html')

    def render(self, context):
        try:
            field = self.field.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        label_class_names = []
        if field.field.required:
            label_class_names.append('required')

        widget_class_name = field.field.widget.__class__.__name__.lower()
        if widget_class_name == 'checkboxinput':
            label_class_names.append('vCheckboxLabel')

        class_str = label_class_names and \
            six.u(' ').join(label_class_names) or six.u('')

        context.push()
        context.push()
        context['class'] = class_str
        context['formfield'] = field
        output = self.get_template(
            field.field.widget.__class__.__name__.lower()).render(context)
        context.pop()
        context.pop()
        return output
