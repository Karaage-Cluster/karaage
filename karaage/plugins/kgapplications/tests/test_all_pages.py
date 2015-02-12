# Copyright 2015 VPAC
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

"""Test all pages render (without exceptions)."""

from __future__ import print_function, unicode_literals

import datetime

from karaage.tests.client import TestAllPagesCase

from ..models import Application


class TestKgApplicationPages(TestAllPagesCase):

    """Discover all URLs, do a HTTP GET and
    confirm 200 OK and no DB changes."""

    fixtures = [
        'test_karaage.json',
        'test_kgapplications.json',
    ]
    variables = {
        'application_id': '1',
        'applicant_id': '1',
        'project_id': '1',
        'token': '27e889413e2d302b9b2a66c63b208962a3788730',
        'state': 'D',
        'label': 'woof',
    }
    module = "karaage.plugins.kgapplications"

    def setUp(self):
        super(TestKgApplicationPages, self).setUp()

        # we have to make sure the application isn't expired
        new_expires = datetime.datetime.now() + datetime.timedelta(days=7)
        Application.objects.all().update(expires=new_expires)
