# This file is part of Karaage.
# Copyright 2014-2015 VPAC
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

from karaage.tests.client import TestAllPagesCase


class TestKgApplicationPages(TestAllPagesCase):

    """Discover all URLs, do a HTTP GET and
    confirm 200 OK and no DB changes."""

    fixtures = [
        'test_karaage.json',
        'test_kgsoftware.json',
    ]
    variables = {
        'software_id': '1',
        'category_id': '1',
        'license_id': '1',
        'version_id': '1',
        'person_id': '1',
    }
    module = "karaage.plugins.kgsoftware"
