# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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

import re
import unittest

import six
from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.core.exceptions import ViewDoesNotExist
from django.test import TestCase
from django.urls import URLPattern, URLResolver
from django.utils import translation
from django.utils.encoding import smart_str
from django.utils.text import slugify

from karaage.middleware.threadlocals import reset


urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [""])


class RegexURLPattern:  # type: ignore
    pass


class RegexURLResolver:  # type: ignore
    pass


class LocaleRegexURLResolver:  # type: ignore
    pass


def describe_pattern(p):
    return str(p.pattern)


def extract_views_from_urlpatterns(urlpatterns, base="", namespace=None):
    """
    Return a list of views from a list of urlpatterns.

    Each object in the returned list is a three-tuple: (view_func, regex, name)
    """
    LANGUAGES = getattr(settings, "LANGUAGES", ((None, None),))

    views = []
    for p in urlpatterns:
        if isinstance(p, (URLPattern, RegexURLPattern)):
            try:
                if not p.name:
                    name = p.name
                elif namespace:
                    name = "{0}:{1}".format(namespace, p.name)
                else:
                    name = p.name
                pattern = describe_pattern(p)
                views.append((p.callback, base + pattern, name))
            except ViewDoesNotExist:
                continue
        elif isinstance(p, (URLResolver, RegexURLResolver)):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            if namespace and p.namespace:
                _namespace = "{0}:{1}".format(namespace, p.namespace)
            else:
                _namespace = p.namespace or namespace
            pattern = describe_pattern(p)
            if isinstance(p, LocaleRegexURLResolver):
                for language in LANGUAGES:
                    with translation.override(language[0]):
                        views.extend(extract_views_from_urlpatterns(patterns, base + pattern, namespace=_namespace))
            else:
                views.extend(extract_views_from_urlpatterns(patterns, base + pattern, namespace=_namespace))
        elif hasattr(p, "_get_callback"):
            try:
                views.append((p._get_callback(), base + describe_pattern(p), p.name))
            except ViewDoesNotExist:
                continue
        elif hasattr(p, "url_patterns") or hasattr(p, "_get_url_patterns"):
            try:
                patterns = p.url_patterns
            except ImportError:
                continue
            views.extend(extract_views_from_urlpatterns(patterns, base + describe_pattern(p), namespace=namespace))
        else:
            raise TypeError("%s does not appear to be a urlpattern object" % p)
    return views


def make_test_get_function(name, url, url_pattern):
    def test_get(self):
        self.assertEqual(
            self.client.login(username="kgsuper", password="aq12ws"),
            True,
            "Login failed.",
        )
        resp = self.client.get(url, follow=True)
        self.assertIn(
            resp.status_code,
            [200, 400, 403],
            "HTTP Error {}: {} > {}".format(
                resp.status_code,
                url_pattern,
                url,
            ),
        )

    test_get.__name__ = str(name)
    return test_get


class TestAllPagesMeta(type):
    @classmethod
    def _add_test_methods(mcs, attrs, urlpatterns):
        # loop through every URL pattern
        for index, (func, regex, url_name) in enumerate(extract_views_from_urlpatterns(urlpatterns)):

            if "module_exclude" not in attrs:
                attrs["module_exclude"] = None

            if attrs["module_exclude"] is not None:
                if func.__module__.startswith("%s." % attrs["module_exclude"]):
                    continue
                elif func.__module__ == attrs["module_exclude"]:
                    continue
                else:
                    pass

            if func.__module__.startswith("%s." % attrs["module"]):
                pass
            elif func.__module__ == attrs["module"]:
                pass
            else:
                continue

            if hasattr(func, "__name__"):
                func_name = func.__name__
            elif hasattr(func, "__class__"):
                func_name = "%s()" % func.__class__.__name__
            else:
                func_name = re.sub(r" at 0x[0-9a-f]+", "", repr(func))

            url_pattern = smart_str(simplify_regex(regex))
            name = "_".join(
                [
                    "test",
                    func.__module__.replace(".", "_"),
                    slugify("%s" % func_name),
                ]
                + slugify(url_pattern.replace("/", "_") or "root").replace("_", " ").split(),
            )
            url = url_pattern

            for key, value in attrs["variables"].items():
                url = url.replace("<%s>" % key, value)

            # bail out if we don't know how to visit this URL properly
            testfunc = unittest.skipIf(
                any(
                    re.search(stop_pattern, url)
                    for stop_pattern in [
                        r"<.*>",
                    ]
                ),
                "URL pattern %r contains stop pattern." % url,
            )(
                make_test_get_function(name, url, url_pattern),
            )

            attrs[name] = testfunc

    def __new__(mcs, name, parents, attrs):
        if parents != (TestCase,):
            mcs._add_test_methods(attrs, urlconf.urlpatterns)
        return super(TestAllPagesMeta, mcs).__new__(mcs, name, parents, attrs)


@six.add_metaclass(TestAllPagesMeta)
class TestAllPagesCase(TestCase):
    def setUp(self):
        super(TestAllPagesCase, self).setUp()

        def cleanup():
            reset()

        self.addCleanup(cleanup)
