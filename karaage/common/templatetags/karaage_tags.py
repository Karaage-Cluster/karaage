# Copyright 2007-2013 VPAC
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
import datetime
from decimal import Decimal

from django import template
from django.conf import settings

from django.http import QueryDict
from django import template
from django.contrib.contenttypes.models import ContentType

from karaage.common.models import Comment

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

@register.inclusion_tag('comments.html')
def comments(obj):
    """ Render comments for obj. """
    content_type = ContentType.objects.get_for_model(obj.__class__)
    comment_list = Comment.objects.filter(
            content_type=content_type,
            object_pk=obj.pk
    )
    return {
        'obj': obj,
        'comment_list': comment_list,
    }

@register.simple_tag
def comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    comment_list = Comment.objects.filter(
            content_type=content_type,
            object_pk=obj.pk
    )
    return int(comment_list.count())

@register.simple_tag
def active(request, pattern):
    import re
    if re.search('^%s/%s' % (request.META['SCRIPT_NAME'], pattern), request.path):
        return 'active'
    return ''



@register.simple_tag
def date_filter(start, end):
    today = datetime.date.today()

    last_7 = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    last_90 = (today - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    last_365 = (today - datetime.timedelta(days=365)).strftime('%Y-%m-%d')


    view_7, view_90, view_365 = False, False, False

    if end == today:
        if start == today - datetime.timedelta(days=7):
            view_7 = True
        if start == today - datetime.timedelta(days=90):
            view_90 = True
        if start == today - datetime.timedelta(days=365):
            view_365 = True

    s = ''

    if view_7:
        s += 'Last 7 Days'
    else:
        s += """<a href="./?start=%s">Last 7 Days</a>""" % last_7
    s += " | "

    if view_90:
        s += "Last 90 Days"
    else:
        s += """<a href="./?start=%s">Last 90 Days</a>""" % last_90
    s += " | "
    if view_365:
        s += "Last 365 Days"
    else:
        s += """<a href="./?start=%s">Last 365 Days</a>""" % last_365


    return s


@register.simple_tag
def yes_no_img(boolean, reversed=False, alt_true='Active', alt_false='Not Active'):
    if reversed == 'reversed':
        if boolean:
            boolean = False
        else:
            boolean = True

    if boolean:
        return """<img src="%simg/icon-yes.gif" alt="%s" />""" % (settings.STATIC_URL, alt_true)
    else:
        return """<img src="%simg/icon-no.gif" alt="%s"/>""" % (settings.STATIC_URL, alt_false)



@register.tag
def searchform(parser, token):
    try:
        tag_name, post_url = token.split_contents()
    except:
        try:
            tag_name = token.split_contents()
            post_url = '.'
        except:
            raise template.TemplateSyntaxError, "%r tag requires one or no arguments" % token.contents.split()[0]
    return SearchFormNode(post_url)


class SearchFormNode(template.Node):
    def __init__(self, post_url):
        self.post_url = post_url

    def render(self, context):
        template_obj = template.loader.get_template('search_form.html')
        context.push()
        context['post_url'] = self.post_url
        output = template_obj.render(context)
        context.pop()
        return output


@register.tag
def gen_table(parser, token):
    try:
        tag_name, queryset, template_name = token.split_contents()
    except:
        try:
            tag_name, queryset = token.split_contents()
            template_name = None
        except:
            raise template.TemplateSyntaxError, "%r tag requires one or two arguments" % token.contents.split()[0]
    return QuerySetTableNode(queryset, template_name)


class QuerySetTableNode(template.Node):

    def __init__(self, queryset, template_name):
        self.queryset = template.Variable(queryset)
        self.template_name = template_name

    def render(self, context):
        try:
            queryset = self.queryset.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if not self.template_name:
            app_label = queryset.model._meta.app_label
            model_name = queryset.model._meta.verbose_name
            template_name = '%s/%s_table.html' % (app_label, model_name.lower().replace(' ', ''))
        else:
            template_name  = self.template_name
        template_obj = template.loader.get_template(template_name)

        context.push()
        context['object_list'] = queryset
        output = template_obj.render(context)
        context.pop()
        return output

@register.simple_tag
def divide(a, b):
    TWOPLACES = Decimal(10) ** -2
    try:
        return (Decimal(a) / Decimal(b) * 100).quantize(TWOPLACES)
    except:
        return ''
