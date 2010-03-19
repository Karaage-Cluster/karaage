# Copyright 2007-2010 VPAC
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
from django.contrib.contenttypes.models import ContentType

def unique(seq):
    """Makes a list unique"""
    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()



def get_date_range(request, default_start=(datetime.date.today()-datetime.timedelta(days=90)), default_end=datetime.date.today()):

    today = datetime.date.today()

    if request.REQUEST.has_key('start'):
        try:
            years, months, days = request.GET['start'].split('-')
            start = datetime.datetime(int(years), int(months), int(days))
            start = start.date()
        except:
            start = today - datetime.timedelta(days=90)
    else:
        start = default_start

    if request.REQUEST.has_key('end'):
        try:
            years, months, days = request.GET['end'].split('-')
            end = datetime.datetime(int(years), int(months), int(days))
            end = end.date()
        except:
            end = today
    else:
        end = default_end

    return start, end




def log_object(user, object, flag, message):

    user.logentry_set.create(
        content_type = ContentType.objects.get_for_model(object.__class__),
        object_id=object._get_pk_val(),
        object_repr=object.__unicode__(),
        action_flag=flag,
        change_message=message
        )
    
