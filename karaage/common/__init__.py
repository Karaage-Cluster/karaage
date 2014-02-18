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

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from karaage.middleware.threadlocals import get_current_user
from karaage.common.forms import CommentForm
from karaage.common.models import LogEntry

from django.template import add_to_builtins
add_to_builtins('karaage.common.templatetags.karaage_tags')


def get_date_range(request, default_start=(datetime.date.today() - datetime.timedelta(days=90)), default_end=datetime.date.today()):

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


def log(user, object, flag, message):
    if user is None:
        user = get_current_user()
    if user is None:
        user_id = None
    else:
        user_id = user.pk
    LogEntry.objects.log_action(
        user_id         = user_id,
        content_type_id = ContentType.objects.get_for_model(object).pk,
        object_id       = object.pk,
        object_repr     = unicode(object),
        action_flag=flag,
        change_message=message)


def new_random_token():
    import random
    from hashlib import sha1
    from django.conf import settings
    # Use the system (hardware-based) random number generator if it exists.
    if hasattr(random, 'SystemRandom'):
        randrange = random.SystemRandom().randrange
    else:
        randrange = random.randrange
    MAX_KEY = 18446744073709551616L     # 2 << 63
    return sha1("%s%s" % (randrange(0, MAX_KEY), settings.SECRET_KEY)).hexdigest()


def log_list(request, breadcrumbs, obj):
    log_list = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(obj.__class__),
        object_id=obj.pk
    )
    paginator = Paginator(log_list, 50)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    return render_to_response(
            'log_list.html',
            { 'short': True, 'obj': obj,
                'page_obj': page_obj,
                'breadcrumbs': breadcrumbs,
            },
            context_instance=RequestContext(request))


def add_comment(request, breadcrumbs, obj):
    form = CommentForm(data=request.POST or None, obj=obj, instance=None)
    if request.method == 'POST':
        form.save(request=request)
        return HttpResponseRedirect(obj.get_absolute_url())

    return render_to_response(
            'add_comment.html',
            { 'form': form, 'obj': obj,
                'breadcrumbs': breadcrumbs,
            },
            context_instance=RequestContext(request))


def is_password_strong(password, old_password=None):
    """Return True if password valid"""
    try:
        from crack import VeryFascistCheck
    except ImportError:
        def VeryFascistCheck(password, old=None):
            if old and password == old:
                return False
            elif len(password) < 6:
                return False
            return True
    try:
        VeryFascistCheck(password, old=old_password)
    except:
        return False

    return True

def is_admin(request):
    if settings.ADMIN_IGNORED:
        return False
    if not request.user.is_authenticated():
        return False
    return request.user.is_admin
