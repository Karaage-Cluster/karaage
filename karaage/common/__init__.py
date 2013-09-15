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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from andsome.middleware.threadlocals import get_current_user

from karaage.common.forms import CommentForm
from karaage.admin.models import LogEntry

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


def log_object(user, object, flag, message):
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


def add_comment(request, content_type, content_url, short_title, obj):
    form = CommentForm(data=request.POST or None, obj=obj, instance=None)
    if request.method == 'POST':
        form.save(request=request)
        return HttpResponseRedirect(obj.get_absolute_url())

    return render_to_response(
            'add_comment.html',
            { 'form': form, 'obj': obj,
                'content_type': content_type,
                'content_url': content_url,
                'short_title': short_title },
            context_instance=RequestContext(request))
