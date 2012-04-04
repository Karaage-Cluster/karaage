# Copyright 2011 VPAC
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


import django_xmlrpc.decorators as decorators
import karaage.machines.models as models
import GeoIP
import re
import ipaddr
import datetime


def process_entry(datetime, machine, host, remain):
        RE_IP = "[0-9:\.]+"
        RE_HOST = "[a-z0-9\.-]+"
        RE_USER = "[a-zA-Z0-9\.!@#_-]+\$?"

        # AUTHENTICATION PASSED
        m = re.match('Accepted (publickey|password) for (%s) from (%s) port (\d+) ssh2$'%(RE_USER,RE_IP), remain)
        if m is not None:
            auth = m.group(1)
            username = m.group(2)
            ip = m.group(3)
            port = int(m.group(4))

            gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

            country = gi.country_code_by_addr(ip)
            subnet = ipaddr.IPv4Network("%s/%d"%(ip, gi.last_netmask()))
            org = "%s/%s"%(subnet.network,subnet.prefixlen)
            print "%s %s %s %s %s %s %s"%(datetime, host, username, auth, ip, country, org)

            useraccount = models.UserAccount.objects.get(username=username)

            log_list = models.UserAccountLog.objects.filter(ua=useraccount, machine=machine, dt=datetime, hostname=host, ip=ip)
            if log_list.count() < 1:
                ual = models.UserAccountLog(
                    ua = useraccount,
                    machine = machine,
                    dt = datetime,
                    hostname = host,
                    authentication_type = auth,
                    ip = ip,
                    country = country,
                    subnet = str(subnet.network),
                    subnet_prefix_len = subnet.prefixlen
                )
                ual.save()

def parse_time(datetime_string):

    month,day,time = datetime_string.split()
    hour,minute,second = time.split(":")

    month = month.lower()

    if month == "jan": month=1
    elif month == "feb": month=2
    elif month == "mar": month=3
    elif month == "apr": month=4
    elif month == "may": month=5
    elif month == "jun": month=6
    elif month == "jul": month=7
    elif month == "aug": month=8
    elif month == "sep": month=9
    elif month == "oct": month=10
    elif month == "nov": month=11
    elif month == "dec": month=12
    else: raise RuntimeError("Unknown month %s"%month)

    day=int(day)
    hour=int(hour)
    minute=int(minute)
    second=int(second)

    return datetime.datetime(
        year=datetime.datetime.now().year,
        month=month, day=day, hour=hour, minute=minute, second=second
    )

@decorators.xmlrpc_func(returns='string', args=['string','string', 'string'])
@decorators.permission_required(perm='projects.change_project')
def user_account_log(username, machine_name, data):

    machine = models.Machine.objects.get(name=machine_name)
    for line in data:
        ok = False

        if not ok:
            m = re.match('([A-Za-z]+ *\d+ \d+:\d+:\d+) ([a-z0-9-]+) ([a-z]+)(\[([0-9]+)\])?: (.*)$', line)
            if m is not None:
                ok = True
                num = 1
                (datetime_string, host, process, pid, remain) = (m.group(1),m.group(2),m.group(3),m.group(5),m.group(6))
                datetime = parse_time(datetime_string)
                process_entry(datetime, machine, host, remain)


        if not ok:
            m = re.match('([A-Za-z]+ *\d+ \d+:\d+:\d+) last message repeated (\d+) times$', line)
            if m is not None:
                ok = True
                datetime_string = m.group(1)
                datetime = parse_time(datetime_string)
                total_num = int(m.group(2))
                if num is not None:
                    while num < total_num:
                        process_entry(datetime, machine, host, remain)
                        num = num + 1

    return [ "Amazing. It didn't work in the best possible way. It really worked." ]

