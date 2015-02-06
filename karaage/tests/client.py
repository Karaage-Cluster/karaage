# Copyright 2014 VLSCI
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

import six
import re
import unittest

from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.test import TestCase
from django.utils.text import slugify
from django.utils.encoding import smart_text

from django_extensions.management.commands.show_urls import \
    extract_views_from_urlpatterns

urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])


def make_test_get_function(name, url, url_pattern):
    def test_get(self):
        self.assertEqual(
            self.client.login(username='kgsuper', password='aq12ws'),
            True,
            'Login failed.',
        )
        resp = self.client.get(url, follow=True)
        self.assertIn(
            resp.status_code,
            [200, 400, 403],
            'HTTP Error {}: {} > {}'.format(
                resp.status_code,
                url_pattern,
                url,
            ),
        )
    test_get.__name__ = str(name)
    return test_get


class TestAllPagesMeta(type):
    @classmethod
    def _add_test_methods(cls, attrs, urlpatterns):
        # loop through every URL pattern
        for index, (func, regex, url_name) in enumerate(
                extract_views_from_urlpatterns(urlpatterns)):

            if func.__module__.startswith("%s." % attrs['module']):
                pass
            elif func.__module__ == attrs['module']:
                pass
            else:
                continue

            if hasattr(func, '__name__'):
                func_name = func.__name__
            elif hasattr(func, '__class__'):
                func_name = '%s()' % func.__class__.__name__
            else:
                func_name = re.sub(r' at 0x[0-9a-f]+', '', repr(func))

            url_pattern = smart_text(simplify_regex(regex))
            name = '_'.join(
                [
                    'test',
                    func.__module__.replace('.', '_'),
                    slugify('%s' % func_name),
                ] + slugify(
                    url_pattern.replace('/', '_') or 'root'
                ).replace('_', ' ').split(),
            )
            url = url_pattern

            for key, value in attrs['variables'].items():
                url = url.replace('<%s>' % key, value)

            # bail out if we don't know how to visit this URL properly
            testfunc = unittest.skipIf(
                any(
                    re.search(stop_pattern, url)
                    for stop_pattern
                    in [
                        r'<.*>',
                    ]
                ),
                'URL pattern %r contains stop pattern.' % url,
            )(
                make_test_get_function(name, url, url_pattern),
            )

            attrs[name] = testfunc

    def __new__(cls, name, parents, attrs):
        if parents != (TestCase,):
            cls._add_test_methods(attrs, urlconf.urlpatterns)
        return super(TestAllPagesMeta, cls).__new__(cls, name, parents, attrs)


@six.add_metaclass(TestAllPagesMeta)
class TestAllPagesCase(TestCase):
    pass
