# Copyright 2014-2015 VPAC
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

try:
    # Python 3
    import xmlrpc.client as xmlrpclib
except ImportError:
    # Python 2
    import xmlrpclib

import datetime
import os.path
import json

from alogger import get_parser
import alogger.tests.examples

from django.test import TestCase

from karaage.tests.test_xmlrpc import DjangoTestClientTransport
from karaage.people.models import Person
from karaage.projects.models import Project
from karaage.institutes.models import Institute
from karaage.machines.models import Account, MachineCategory


class XmlrpcTestCase(TestCase):
    fixtures = [
        'test_karaage.json',
    ]

    def setUp(self):
        super(XmlrpcTestCase, self).setUp()
        self.server = xmlrpclib.ServerProxy(
            'http://testserver/xmlrpc/',
            transport=DjangoTestClientTransport(self.client),
        )

    def test_parse_usage(self):
        server = self.server
        today = datetime.datetime.today()
        today = today.strftime("%Y-%m-%d")

        module_file = alogger.tests.examples.__file__
        directory = os.path.abspath(os.path.split(module_file)[0])
        path = os.path.join(directory, "torque.log")
        fd = open(path, "r")
        lines = fd.readlines()
        fd.close()

        with self.assertRaises(xmlrpclib.Fault) as cm:
            server.parse_usage(
                "tango", "aqws12",
                lines, today, 'tango', 'TORQUE')

        self.assertEqual(cm.exception.faultCode, 81)
        self.assertEqual(
            cm.exception.faultString, 'Username and/or password is incorrect')

        mc = MachineCategory.objects.get(name="Default")
        proj = Project.objects.get(pid="TestProject1")
        i = Institute.objects.get(name="Example")

        proj2 = Project.objects.create(pid="pMona0041", institute=i)

        p = Person.objects.create(
            username="blair", short_name="B", full_name="Blair",
            institute=i)
        proj.group.members.add(p)
        Account.objects.create(
            username="blair", person=p, machine_category=mc,
            default_project=proj,
            date_created=datetime.datetime.today())

        p = Person.objects.create(
            username="philipn", short_name="Phil", full_name="Phillip",
            institute=i)
        proj.group.members.add(p)
        proj2.group.members.add(p)
        Account.objects.create(
            username="philipn", person=p, machine_category=mc,
            default_project=proj,
            date_created=datetime.datetime.today())

        result = server.parse_usage(
            "tango", "aq12ws",
            lines, today, 'tango', 'TORQUE')
        self.assertEqual(
            result[0],
            'Inserted : 16\nUpdated  : 0\nFailed   : 6\nSkiped   : 35')

    def test_parse_usage_alogger(self):
        server = self.server
        today = datetime.datetime.today()
        today = today.strftime("%Y-%m-%d")

        module_file = alogger.tests.examples.__file__
        directory = os.path.abspath(os.path.split(module_file)[0])
        path = os.path.join(directory, "torque.log")
        fd = open(path, "r")
        lines = fd.readlines()
        fd.close()

        mc = MachineCategory.objects.get(name="Default")
        proj = Project.objects.get(pid="TestProject1")
        i = Institute.objects.get(name="Example")

        proj2 = Project.objects.create(pid="pMona0041", institute=i)

        p = Person.objects.create(
            username="blair", short_name="B", full_name="Blair",
            institute=i)
        proj.group.members.add(p)
        Account.objects.create(
            username="blair", person=p, machine_category=mc,
            default_project=proj,
            date_created=datetime.datetime.today())

        p = Person.objects.create(
            username="philipn", short_name="Phil", full_name="Phillip",
            institute=i)
        proj.group.members.add(p)
        proj2.group.members.add(p)
        Account.objects.create(
            username="philipn", person=p, machine_category=mc,
            default_project=proj,
            date_created=datetime.datetime.today())

        json_array = []

        parser = get_parser("TORQUE")
        for line in lines:
            d = parser.line_to_dict(line)
            if d is None:
                continue

            json_array.append(json.dumps(d))

        result = server.parse_usage(
            "tango", "aq12ws",
            json_array, today, 'tango', 'alogger')
        self.assertEqual(
            result[0],
            'Inserted : 16\nUpdated  : 0\nFailed   : 6\nSkiped   : 0')

    def test_add_modules_used(self):
        server = self.server
        today = datetime.datetime.today()
        today = today.strftime("%Y-%m-%d")

        with self.assertRaises(xmlrpclib.Fault) as cm:
            server.add_modules_used(
                "tango", "aqws12",
                "jobid", [], today)

        self.assertEqual(cm.exception.faultCode, 81)
        self.assertEqual(
            cm.exception.faultString, 'Username and/or password is incorrect')

        result = server.add_modules_used(
            "tango", "aq12ws",
            "942337.tango-m.vpac.org", [
                "modules", "pgi/12.10", "gmp/5.0.5", "mpfr/3.1.1", "mpc/1.0",
                "gcc/4.7.2", "intel/12.1.3", "openmpi-pgi/1.6.3",
                "vpac/config", "lapack/3.4.2", "octave/3.6.3"],
            today
        )
        self.assertEqual(result, True)

        multicall = xmlrpclib.MultiCall(server)

        multicall.add_modules_used(
            "tango", "aq12ws",
            "942337.tango-m.vpac.org", [
                "modules", "pgi/12.10", "gmp/5.0.5", "mpfr/3.1.1", "mpc/1.0",
                "gcc/4.7.2", "intel/12.1.3", "openmpi-pgi/1.6.3",
                "vpac/config", "lapack/3.4.2", "octave/3.6.3"],
            today
        )

        multicall.add_modules_used(
            "tango", "aq12ws",
            "942338.tango-m.vpac.org", [
                "modules", "pgi/12.10", "gmp/5.0.5", "mpfr/3.1.1", "mpc/1.0",
                "gcc/4.7.2", "intel/12.1.3", "openmpi-pgi/1.6.3",
                "vpac/config", "lapack/3.4.2", "octave/3.6.3"],
            today
        )

        result = tuple(multicall())
        self.assertEqual(result, (True, True))
