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

import datetime
import importlib
import warnings

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q

from karaage.middleware.threadlocals import get_current_user
from karaage.common.forms import CommentForm
from karaage.common.models import (LogEntry, ADDITION, CHANGE,
                                   DELETION, COMMENT)


from django.template import add_to_builtins
add_to_builtins('karaage.common.templatetags.karaage_tags')


def get_date_range(request, default_start=None, default_end=None):

    if default_start is None:
        default_start = datetime.date.today() - datetime.timedelta(days=90)
    if default_end is None:
        default_end = datetime.date.today()

    today = datetime.date.today()

    if 'start' in request.REQUEST:
        try:
            years, months, days = request.GET['start'].split('-')
            start = datetime.datetime(int(years), int(months), int(days))
            start = start.date()
        except:
            start = today - datetime.timedelta(days=90)
    else:
        start = default_start

    if 'end' in request.REQUEST:
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
    def __init__(self, user, object, flag, message):
        warnings.warn("Calling karaage.common.log directly has been"
                      " deprecated. You should use the API "
                      "log.(add|change|field_change|delete|comment)",
                      DeprecationWarning)
        LogEntry.objects.log_object(object, flag, message, user)

    @classmethod
    def add(cls, object, message, user=None):
        return LogEntry.objects.log_object(object, ADDITION, message, user)

    @classmethod
    def change(cls, object, message, user=None):
        return LogEntry.objects.log_object(object, CHANGE, message, user)

    @classmethod
    def field_change(cls, object, user=None, field=None, new_value=None):
        return LogEntry.objects.log_object(
            object, CHANGE, 'Changed %s to %s' % (field, new_value), user)

    @classmethod
    def delete(cls, object, message, user=None):
        return LogEntry.objects.log_object(object, DELETION, message, user)

    @classmethod
    def comment(cls, object, message, user=None):
        return LogEntry.objects.log_object(object, COMMENT, message, user)


def new_random_token():
    import random
    from hashlib import sha1
    # Use the system (hardware-based) random number generator if it exists.
    if hasattr(random, 'SystemRandom'):
        randrange = random.SystemRandom().randrange
    else:
        randrange = random.randrange
    MAX_KEY = 18446744073709551616L     # 2 << 63

    string = "%s%s" % (randrange(0, MAX_KEY), settings.SECRET_KEY)
    return sha1(string).hexdigest()


def log_list(request, breadcrumbs, obj):
    log_list = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(obj.__class__),
        object_id=obj.pk
    )

    if 'search' in request.REQUEST:
        terms = request.REQUEST['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(user__username__iexact=term)
            q = q | Q(object_repr__iexact=term)
            q = q | Q(change_message__icontains=term)
            query = query & q

        log_list = log_list.filter(query)
    else:
        terms = ""

    paginator = Paginator(log_list, 50)

    page = request.GET.get('page')
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    return render_to_response(
        'common/log_list.html',
        {
            'short': True, 'obj': obj,
            'page': page,
            'breadcrumbs': breadcrumbs,
            'terms': terms,
        },
        context_instance=RequestContext(request))


def add_comment(request, breadcrumbs, obj):
    assert obj is not None
    assert obj.pk is not None
    form = CommentForm(data=request.POST or None, obj=obj, instance=None)
    if request.method == 'POST':
        form.save(request=request)
        return HttpResponseRedirect(obj.get_absolute_url())

    return render_to_response(
        'common/add_comment.html',
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


def get_hooks(name):
    for app in settings.INSTALLED_APPS:
        try:
            module_name = app + ".hooks"
            module = importlib.import_module(module_name)
        except ImportError:
            pass
        else:
            function = getattr(module, name, None)
            if function is not None:
                yield function


def get_urls(name):
    for app in settings.INSTALLED_APPS:
        try:
            module_name = app + ".urls"
            module = importlib.import_module(module_name)
        except ImportError:
            pass
        else:
            urls = getattr(module, name, None)
            if urls is not None:
                yield urls
