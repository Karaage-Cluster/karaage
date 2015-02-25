#!/usr/bin/env python

# Copyright 2010, 2014-2015 VPAC
# Copyright 2010, 2014 The University of Melbourne
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
"""Karaage setup script."""

from setuptools import setup
import os


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

dirs = ['karaage', ]
packages = []
for d in dirs:
    for dirpath, dirnames, filenames in os.walk(d):
        # Ignore dirnames that start with '.'
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'):
                del dirnames[i]
        if filenames:
            packages.append('.'.join(fullsplit(dirpath)))

tests_require = [
    "django-extensions",
    "factory_boy",
    "mock",
    "cracklib",
]

setup(
    name="karaage4",
    version=open('VERSION.txt', 'r').readline().strip(),
    url='https://github.com/Karaage-Cluster/karaage',
    author='Brian May',
    author_email='brian@v3.org.au',
    description='Collection of Django apps to manage a clusters',
    packages=packages,
    license="GPL3+",
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public "
            "License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="karaage cluster user administration",
    package_data={
        '': ['*.css', '*.html', '*.js', '*.png', '*.gif', '*.map', '*.txt',
             '*.json'],
    },
    scripts=[
        'sbin/kg_set_secret_key',
        'sbin/kg-manage',
        'sbin/kg-migrate-south',
    ],
    data_files=[
        ('/etc/karaage3',
            ['conf/settings.py', 'conf/karaage.wsgi']),
        ('/etc/apache2/conf-available',
            ['conf/karaage3-wsgi.conf']),
    ],
    install_requires=[
        "cssmin",
        "Django >= 1.7",
        "python-alogger >= 2.0",
        "django-xmlrpc >= 0.1",
        "django-simple-captcha",
        "django-ajax-selects >= 1.1.3",
        "django_jsonfield >= 0.9.12",
        "django-model-utils >= 2.0.0",
        "python-tldap >= 0.3.3",
        "django-pipeline",
        "django-tables2",
        "django-filter",
        "six",
        "slimit>=0.8.1",
    ],
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
        'applications': [
            # no dependencies for kgapplications
        ],
        'software': [
            "karaage4[applications]",
            "karaage4[usage]",
        ],
        'usage': [
            "karaage4[software]",
            "django_celery",
            "django-filter",
            "matplotlib",
        ],
    },
)
