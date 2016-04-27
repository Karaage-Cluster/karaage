# Copyright 2008, 2010-2011, 2013-2015 VPAC
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

import datetime
import importlib
import warnings
import six

import django
from django.http import QueryDict
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from karaage.plugins import BasePlugin
from karaage.middleware.threadlocals import get_current_user
from karaage.common.forms import CommentForm
from karaage.common.models import (LogEntry, ADDITION, CHANGE,
                                   DELETION, COMMENT)


def get_date_range(request, default_start=None, default_end=None):

    if default_start is None:
        default_start = datetime.date.today() - datetime.timedelta(days=90)
    if default_end is None:
        default_end = datetime.date.today()

    today = datetime.date.today()

    if 'start' in request.GET:
        try:
            years, months, days = request.GET['start'].split('-')
            start = datetime.datetime(int(years), int(months), int(days))
            start = start.date()
        except:
            start = today - datetime.timedelta(days=90)
    else:
        start = default_start

    if 'end' in request.GET:
        try:
            years, months, days = request.GET['end'].split('-')
            end = datetime.datetime(int(years), int(months), int(days))
            end = end.date()
        except:
            end = today
    else:
        end = default_end

    return start, end


def get_current_person():
    user = get_current_user()
    if user is None:
        return None
    if not user.is_authenticated():
        return None
    return user


class log():

    def __init__(self, user, obj, flag, message):
        warnings.warn("Calling karaage.common.log directly has been"
                      " deprecated. You should use the API "
                      "log.(add|change|field_change|delete|comment)",
                      DeprecationWarning)
        LogEntry.objects.log_object(obj, flag, message, user)

    @classmethod
    def add(cls, obj, message, user=None):
        return LogEntry.objects.log_object(obj, ADDITION, message, user)

    @classmethod
    def change(cls, obj, message, user=None):
        return LogEntry.objects.log_object(obj, CHANGE, message, user)

    @classmethod
    def field_change(cls, obj, user=None, field=None, new_value=None):
        return LogEntry.objects.log_object(
            obj, CHANGE, 'Changed %s to %s' % (field, new_value), user)

    @classmethod
    def delete(cls, obj, message, user=None):
        return LogEntry.objects.log_object(obj, DELETION, message, user)

    @classmethod
    def comment(cls, obj, message, user=None):
        return LogEntry.objects.log_object(obj, COMMENT, message, user)


def new_random_token():
    import random
    from hashlib import sha1
    # Use the system (hardware-based) random number generator if it exists.
    if hasattr(random, 'SystemRandom'):
        randrange = random.SystemRandom().randrange
    else:
        randrange = random.randrange
    max_key = 18446744073709551616     # 2 << 63

    string = six.u("%s%s") % (randrange(0, max_key), settings.SECRET_KEY)
    return sha1(string.encode("ascii")).hexdigest()


def log_list(request, breadcrumbs, obj):
    result = QueryDict("", mutable=True)
    result['content_type'] = ContentType.objects.get_for_model(obj).pk
    result['object_id'] = obj.pk
    url = reverse('kg_log_list') + "?" + result.urlencode()
    return HttpResponseRedirect(url)


def add_comment(request, breadcrumbs, obj):
    assert obj is not None
    assert obj.pk is not None
    form = CommentForm(
        data=request.POST or None, obj=obj,
        request=request, instance=None)
    if request.method == 'POST':
        form.save()
        return HttpResponseRedirect(obj.get_absolute_url())

    return render_to_response(
        'karaage/common/add_comment.html',
        {
            'form': form, 'obj': obj,
            'breadcrumbs': breadcrumbs,
        },
        context_instance=RequestContext(request))


def is_admin(request):
    if settings.ADMIN_IGNORED:
        return False
    if not request.user.is_authenticated():
        return False
    return request.user.is_admin


def get_app_modules(name):
    if django.VERSION < (1, 7):
        for app in settings.INSTALLED_APPS:
            try:
                module_name = app + "." + name
                module = importlib.import_module(module_name)
                yield module
            except ImportError:
                pass
    else:
        from django.apps import apps
        for config in apps.get_app_configs():
            if isinstance(config, BasePlugin):
                module_name = config.name + "." + name
                module = importlib.import_module(module_name)
                yield module


def get_urls(name):
    for module in get_app_modules("urls"):
        urls = getattr(module, name, None)
        if urls is not None:
            yield urls
