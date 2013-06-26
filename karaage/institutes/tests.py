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

from django.test import TestCase
from django.core.management import call_command

from tldap.test import slapd

from karaage.institutes.models import Institute
from karaage.test_data.initial_ldap_data import test_ldif

from karaage.datastores import ldap_schemas

class InstituteTestCase(TestCase):

    def setUp(self):
        server = slapd.Slapd()
        server.set_port(38911)
        server.start()
        server.ldapadd("\n".join(test_ldif)+"\n")
        call_command('loaddata', 'karaage/testproject/karaage_data', **{'verbosity': 0})

        self.server = server

    def tearDown(self):
        self.server.stop()


    def test_add(self):
        institute = Institute.objects.create(name='TestInstitute54')
        
        lgroup = ldap_schemas.group.objects.get(cn=institute.group.name)
        self.assertEqual(institute.name.lower().replace(' ' , ''), lgroup.cn)


    def test_add_spaces(self):
        institute = Institute.objects.create(name='Test Institute 60')
        
        lgroup = ldap_schemas.group.objects.get(cn=institute.group.name)
        self.assertEqual(institute.name.lower().replace(' ' , ''), lgroup.cn)

    def test_add_existing_name(self):
        
        lgroup = ldap_schemas.group()
        lgroup.set_defaults()
        lgroup.cn = 'testinstitute27'
        lgroup.pre_create(master=None)
        lgroup.pre_save()
        lgroup.save()

        institute = Institute.objects.create(name='Test Institute 27')

        lgroup = ldap_schemas.group.objects.get(cn=institute.group.name)
        self.assertEqual(institute.name.lower().replace(' ' , ''), lgroup.cn) 

    def test_add_existing_gid(self):
        
        lgroup = ldap_schemas.group()
        lgroup.set_defaults()
        lgroup.cn = 'testinstituteother'
        lgroup.pre_create(master=None)
        lgroup.gidNumber = 700
        lgroup.pre_save()
        lgroup.save()

        institute = Institute.objects.create(name='Test Institute Other')
        self.assertEqual(institute.group.name, "testinstituteother")

        lgroup = ldap_schemas.group.objects.get(cn=institute.group.name)
        self.assertEqual(lgroup.gidNumber, 700)
