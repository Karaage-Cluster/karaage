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
from django.template import Library
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import filesizeformat

register = Library()


@register.filter
def timeformat(value):

    if value == '':
        return ''

    if value is None:
        return '0s'
    if value < 60:
        return '%ss' % intcomma(int(value))
    # less than 1 hour
    elif value < 3600:
        v = int(value / 60)
        return '%sm' % intcomma(v)
    # less than 1 day
    # elif value < 86400:
    #    v = int(value/3600)
    #    return '%sh' % intcomma(v)
    # less than a month
    # elif value < 2592000:
    #    v = int(value/86400)
    #    return '%sd' % intcomma(v)
    # less than 1 year
    # elif value < 31104000:
    #    v = int(value/2592000)
    #    return '%smonth' % intcomma(v)
    else:
        v = int(value / 3600)
        return '%sh' % intcomma(v)


@register.filter
def fileformat(kilobytes):
    if kilobytes:
        return filesizeformat(kilobytes * 1024)
    return None
