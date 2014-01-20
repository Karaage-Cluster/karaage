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

from django_xmlrpc.decorators import xmlrpc_func
import datetime

from karaage.usage.pbsmoab import parse_logs
from karaage.common.decorators import xmlrpc_machine_required


@xmlrpc_machine_required()
@xmlrpc_func(returns='string', args=['string', 'date', 'string', 'string'])
def parse_pbsmoab_usage(machine, usage, date, machine_name, log_type):
    """
    Parses usage
    """
    assert machine.name == machine_name

    year, month, day = date.split('-')
    date = datetime.date(int(year), int(month), int(day))

    return parse_logs(usage, date, machine_name, log_type)
