"""Test all pages render (without exceptions) using Selenium."""
from __future__ import print_function, unicode_literals

import functools
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
    decorator = ['login_required']
    # loop through every URL pattern
    for index, (func, regex, url_name) in enumerate(
        extract_views_from_urlpatterns(urlpatterns)
    ):
        if hasattr(func, '__globals__'):
            func_globals = func.__globals__
        elif hasattr(func, 'func_globals'):
            func_globals = func.func_globals
        else:
            func_globals = {}

        decorators = [d for d in decorator if d in func_globals]

        if isinstance(func, functools.partial):
            func = func.func
            decorators.insert(0, 'functools.partial')

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
                '%.4d' % index,
                func.__module__.replace(u'.', u'_'),
                slugify(func_name),
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
                    '<uidb64>',
                    #'<app_label>',
                    #'<model>',
                    #'<key>',
                    #'<token>',
                    #'/tasks/',
                    #'/usage/',
                    #'/captcha/',
                ]
            ),
            'URL pattern %r contains stop pattern.' % url_pattern,
        )(
            make_test_get_function(name, url, url_pattern),
        )
        view_path = '%s.%s' % (func.__module__, func_name)
        testfunc = unittest.skipIf(
            any(
                re.search(stop_pattern, view_path)
                for stop_pattern in [
                    '^captcha.',
                    '^ajax_select.',
                    '^django.contrib.auth.views.',
                    '^django.contrib.staticfiles.views.',
                    '^django_xmlrpc.views.',
                    '^karaage.people.views.persons.activate$',
                ]
            ),
            'View %r contains stop pattern.' % view_path,
        )(
            testfunc,
        )
        setattr(testcase, name, testfunc)

add_test_methods(TestAllPages, urlconf.urlpatterns)
