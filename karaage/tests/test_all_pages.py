"""Test all pages render (without exceptions) using Selenium."""
from __future__ import print_function, unicode_literals

import re
import unittest

from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.test import TestCase
from django.utils.text import slugify
from django.utils.encoding import smart_text

from django_extensions.management.commands.show_urls import \
    extract_views_from_urlpatterns


def make_test_get_function(name, url, url_pattern):
    def test_get(self):
        self.assertEqual(
            self.client.login(username='1', password='password'),
            True,
            'Login failed.',
        )
        resp = self.client.get(url)
        self.assertIn(
            resp.status_code,
            [200, 302, 403],
            'HTTP Error {}: {} > {}'.format(
                resp.status_code,
                url_pattern,
                url,
            ),
        )
    test_get.__name__ = str(name)
    return test_get


class TestAllPages(TestCase):

    """Discover all URLs, do a HTTP GET and confirm 200 OK and no DB changes."""

    fixtures = [
        fixture
        for (app, fixture)
        in [
            ('karaage.apps.Karaage', 'test_karaage.json'),
            ('kgapplications.plugin', 'test_kgapplications.json'),
            ('kgsoftware.plugin', 'test_kgsoftware.json'),
            ('kgusage.plugin', 'test_kgusage.json'),
        ]
        if app in settings.INSTALLED_APPS
    ]


urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])


def add_test_methods(testcase, urlpatterns):
    # loop through every URL pattern
    for index, (func, regex, url_name) in enumerate(
        extract_views_from_urlpatterns(urlpatterns)
    ):
        url_pattern = smart_text(simplify_regex(regex))
        name = '_'.join(
            [
                'test',
                '%.4d' % index,
            ] + slugify(
                url_pattern.replace(u'/', u'_') or u'root'
            ).replace(u'_', u' ').split(),
        )
        url = re.sub('<[\w_]+>', '1', url_pattern)
        # bail out if we don't know how to visit this URL properly
        testfunc = unittest.skipIf(
            any(
                re.search(stop_pattern, url_pattern)
                for stop_pattern
                in [
                    '<app_label>',
                    '<model>',
                    '/tasks/',
                    '/usage/',
                    '/captcha/',
                ]
            ),
            'URL pattern %r contains stop pattern.' % url_pattern,
        )(
            make_test_get_function(name, url, url_pattern),
        )
        setattr(testcase, name, testfunc)

add_test_methods(TestAllPages, urlconf.urlpatterns)
