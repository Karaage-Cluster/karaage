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
import datetime
import os.path
from decimal import Decimal

import django
from django import template
from django.conf import settings
from django.http import QueryDict
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape

from karaage.plugins import BasePlugin
from karaage.common.models import LogEntry, COMMENT

register = template.Library()


class UrlWithParamNode(template.Node):

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
            raise template.TemplateSyntaxError(
                "Argument syntax wrong: should be key=value")
    return UrlWithParamNode(copy, nopage, qschanges)


@register.inclusion_tag('karaage/common/comments.html', takes_context=True)
def comments(context, obj):
    """ Render comments for obj. """
    content_type = ContentType.objects.get_for_model(obj.__class__)
    comment_list = LogEntry.objects.filter(
        content_type=content_type,
        object_id=obj.pk,
        action_flag=COMMENT
    )
    return {
        'obj': obj,
        'comment_list': comment_list,
        'is_admin': context['is_admin'],
    }


@register.simple_tag
def comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    comment_list = LogEntry.objects.filter(
        content_type=content_type,
        object_id=obj.pk,
        action_flag=COMMENT
    )
    return int(comment_list.count())


@register.simple_tag
def active(request, pattern):
    import re
    spec = '^%s/%s' % (request.META['SCRIPT_NAME'], pattern)
    if re.search(spec, request.path):
        return 'active'
    return ''


@register.simple_tag
def date_filter(start, end):
    result = QueryDict("", mutable=True)

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

    s = []

    if view_7:
        s.append('Last 7 Days')
    else:
        result["start"] = last_7
        url = ".?" + result.urlencode()
        s.append("""<a href="%s">Last 7 Days</a>""" % escape(url))

    if view_90:
        s.append("Last 90 Days")
    else:
        result["start"] = last_90
        url = ".?" + result.urlencode()
        s.append("""<a href="%s">Last 90 Days</a>""" % escape(url))

    if view_365:
        s.append("Last 365 Days")
    else:
        result["start"] = last_365
        url = ".?" + result.urlencode()
        s.append("""<a href="%s">Last 365 Days</a>""" % escape(url))

    return " | ".join(s)


@register.simple_tag
def yes_no(boolean, true_msg='Yes', false_msg='No'):
    if reversed == 'reversed':
        if boolean:
            boolean = False
        else:
            boolean = True

    if boolean:
        return "<span class='yes'>%s</span>" % true_msg
    else:
        return "<span class='no'>%s</span>" % false_msg


class SearchFormNode(template.Node):

    def __init__(self, post_url):
        self.post_url = post_url

    def render(self, context):
        template_obj = template.loader.get_template(
            'karaage/common/search_form.html')
        context.push()
        context['post_url'] = self.post_url
        output = template_obj.render(context)
        context.pop()
        return output


@register.simple_tag
def divide(a, b):
    two_places = Decimal(10) ** -2
    try:
        return (Decimal(a) / Decimal(b) * 100).quantize(two_places)
    except:
        return ''


def get_app_labels():
    if django.VERSION < (1, 7):
        for app in settings.INSTALLED_APPS:
            _, _, label = app.rpartition(".")
            if label is not None:
                yield label
    else:
        from django.apps import apps
        for config in apps.get_app_configs():
            if isinstance(config, BasePlugin):
                yield config.label


class ForEachAppIncludeNode(template.Node):

    def __init__(self, template_name):
        self.template_name = template.Variable(template_name)

    def render(self, context):
        template_name = self.template_name.resolve(context)

        result = []
        for label in get_app_labels():
            template_path = os.path.join(label, template_name)
            try:
                template_obj = template.loader.get_template(template_path)
            except template.TemplateDoesNotExist:
                pass
            else:
                context.push()
                output = template_obj.render(context)
                result.append(output)
                context.pop()

        return "".join(result)


@register.tag
def for_each_app_include(parser, token):
    try:
        tag_name, template_name = token.split_contents()
    except:
        raise template.TemplateSyntaxError(
            "%r tag requires one arguments" % token.contents.split()[0])
    return ForEachAppIncludeNode(template_name)


@register.assignment_tag()
def is_for_each_app_include_empty(template_name):
    for label in get_app_labels():
        template_path = os.path.join(label, template_name)
        try:
            template.loader.get_template(template_path)
            return False
        except template.TemplateDoesNotExist:
            pass
    return True
