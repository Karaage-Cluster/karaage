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
    import http.client as httplib
except ImportError:
    # Python 2
    import httplib

try:
    # Python 3
    import xmlrpc.client as xmlrpclib
except ImportError:
    # Python 2
    import xmlrpclib

from django.test import TestCase

from karaage.people.models import Person, Group
from karaage.machines.models import Account
from karaage.projects.models import ProjectQuota


class DjangoTestClientTransport(object):
    client = None

    def __init__(self, client):
        self.client = client

    def getparser(self):
        return xmlrpclib.getparser()

    def request(self, host, handler, request_body, verbose=False):
        parser, unmarshaller = self.getparser()
        response = self.client.post(handler, request_body, 'text/xml')
        if response.status_code != 200:
            raise xmlrpclib.ProtocolError(
                '%s%s' % (host, handler),
                response.status_code,
                httplib.responses.get(response.status_code, ''),
                dict(response.items()),
            )
        parser.feed(response.content)
        return unmarshaller.close()


class XmlrpcTestCase(TestCase):
    fixtures = [
        'test_karaage.json',
    ]

    def get_server_proxy(self):
        return xmlrpclib.ServerProxy(
            'http://testserver/xmlrpc/',
            transport=DjangoTestClientTransport(self.client),
        )

    def setUp(self):
        super(XmlrpcTestCase, self).setUp()
        self.server = self.get_server_proxy()

    def test_get_disk_quota(self):
        server = self.server

        result = server.get_disk_quota("kgtestuser1")
        self.assertEqual(result, "Account not found")

        result = server.get_disk_quota("kgtestuser3")
        self.assertEqual(result, False)
        result = server.get_disk_quota("kgtestuser3", "tango")
        self.assertEqual(result, False)

        account = Account.objects.get(username="kgtestuser3")
        account.disk_quota = 1
        account.save()

        result = server.get_disk_quota("kgtestuser3")
        self.assertEqual(result, 1048576)
        result = server.get_disk_quota("kgtestuser3", "tango")
        self.assertEqual(result, 1048576)

    def test_showquota(self):
        server = self.server

        result = server.showquota("kgtestuser1")
        self.assertEqual(result, [-1, 'Account not found'])

        result = server.showquota("kgtestuser3")
        self.assertEqual(result, [0, [['TestProject1', 0, '0.0', True]]])
        result = server.showquota("kgtestuser3", "tango")
        self.assertEqual(result, [0, [['TestProject1', 0, '0.0', True]]])

        pq = ProjectQuota.objects.get(project__pid="TestProject1")
        pq.cap = 1
        pq.save()

        result = server.showquota("kgtestuser3")
        self.assertEqual(result, [0, [['TestProject1', 0, '1.0', True]]])
        result = server.showquota("kgtestuser3", "tango")
        self.assertEqual(result, [0, [['TestProject1', 0, '1.0', True]]])

    def test_get_projects(self):
        server = self.server

        with self.assertRaises(xmlrpclib.Fault) as cm:
            server.get_projects("tango", "aqws12")
        self.assertEqual(cm.exception.faultCode, 81)
        self.assertEqual(
            cm.exception.faultString, 'Username and/or password is incorrect')

        result = server.get_projects("tango", "aq12ws")
        self.assertEqual(result, ['TestProject1'])

        result = server.get_projects("wexstan", "aq12ws")
        self.assertEqual(result, [])

        result = server.get_projects("edda", "aq12ws")
        self.assertEqual(result, [])

    def test_get_project(self):
        server = self.server

        # account does not exist
        result = server.get_project("kgtestuser1", "TestProject1")
        self.assertEqual(result, "Account 'kgtestuser1' not found")

        # project does exist, and person belongs to it
        result = server.get_project("kgtestuser3", "TestProject1")
        self.assertEqual(result, "TestProject1")

        result = server.get_project(
            "kgtestuser3", "TestProject1", "tango")
        self.assertEqual(result, "TestProject1")

        result = server.get_project("kgtestuser3", "TestProject1", "wexstan")
        self.assertEqual(result, "Account 'kgtestuser3' not found")

        result = server.get_project("kgtestuser3", "TestProject1", "edda")
        self.assertEqual(result, "Account 'kgtestuser3' not found")

        # project does not exist - should fall back to default
        result = server.get_project("kgtestuser3", "TestProjectx", "tango")
        self.assertEqual(result, "TestProject1")

        result = server.get_project("kgtestuser3", "TestProjectx", "wexstan")
        self.assertEqual(result, "Account 'kgtestuser3' not found")

        result = server.get_project("kgtestuser3", "TestProjectx", "edda")
        self.assertEqual(result, "Account 'kgtestuser3' not found")

        # project does exist, and person doesn't belong to it
        # in this case default fall back fails too
        person = Person.objects.get(username="kgtestuser3")
        group = Group.objects.get(name="testproject1")
        group.members.remove(person)

        result = server.get_project("kgtestuser3", "TestProject1")
        self.assertEqual(result, "None")

        result = server.get_project("kgtestuser3", "TestProject1", "tango")
        self.assertEqual(result, "None")

        result = server.get_project("kgtestuser3", "TestProject1", "wexstan")
        self.assertEqual(result, "Account 'kgtestuser3' not found")

        result = server.get_project("kgtestuser3", "TestProject1", "edda")
        self.assertEqual(result, "Account 'kgtestuser3' not found")

    def test_get_project_members(self):
        server = self.server

        with self.assertRaises(xmlrpclib.Fault) as cm:
            server.get_project_members("tango", "aqws12", "TestProject2")
        self.assertEqual(cm.exception.faultCode, 81)
        self.assertEqual(
            cm.exception.faultString, 'Username and/or password is incorrect')

        # Project has no ProjectQuota
        result = server.get_project_members("tango", "aq12ws", "TestProject2")
        self.assertEqual(result, "Project not found")

        result = server.get_project_members(
            "wexstan", "aq12ws", "TestProject2")
        self.assertEqual(result, "Project not found")

        result = server.get_project_members("edda", "aq12ws", "TestProject2")
        self.assertEqual(result, "Project not found")

        # Project has ProjectQuota for default machine category
        result = server.get_project_members("tango", "aq12ws", "TestProject1")
        self.assertEqual(result, ['kgtestuser3'])

        result = server.get_project_members(
            "wexstan", "aq12ws", "TestProject1")
        self.assertEqual(result, "Project not found")

        result = server.get_project_members("edda", "aq12ws", "TestProject1")
        self.assertEqual(result, "Project not found")

    def test_get_users_project(self):
        server = self.server

        with self.assertRaises(xmlrpclib.Fault) as cm:
            server.get_users_projects("tango", "aq12ws")
        self.assertEqual(cm.exception.faultCode, 81)
        self.assertEqual(
            cm.exception.faultString, 'Username and/or password is incorrect')

        result = server.get_users_projects("kgtestuser1", "aq12ws")
        self.assertEqual(result, [0, []])

        result = server.get_users_projects("kgtestuser2", "aq12ws")
        self.assertEqual(result, [0, []])

        result = server.get_users_projects("kgtestuser3", "aq12ws")
        self.assertEqual(result, [0, ['TestProject1']])
