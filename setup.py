#!/usr/bin/env python

# Copyright 2012-2014 VPAC
#
# This file is part of django-tldap.
#
# django-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-tldap  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import os

with open('VERSION.txt', 'r') as f:
    version = f.readline().strip()

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

packages = []
for dirpath, dirnames, filenames in os.walk("karaage"):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        packages.append('.'.join(fullsplit(dirpath)))

setup(
    name = "karaage",
    version = version,
    url = 'https://github.com/Karaage-Cluster/karaage',
    author = 'Brian May',
    author_email = 'brian@vpac.org',
    description = 'Collection of Django apps to manage a clusters',
    license = "GPL3+",
    packages = packages,
    package_data = {
        '': [ '*.css', '*.html', '*.js', '*.png', '*.gif', '*.map', '*.txt' ],
    },
    scripts = [ 'sbin/kg_set_secret_key' ],
    data_files=[
        ('/etc/karaage', [ 'conf/global_settings.py', ]),
    ],
    install_requires = [
        "python > 2.4",
        "Django >= 1.6",
        "South >= 0.7",
        "python-alogger >= 2.0",
        "django-xmlrpc >= 0.1",
        "django-simple-captcha",
        "django-ajax-selects >= 1.1.3",
        "django_jsonfield >= 0.9.12",
        "django-model-utils >= 2.0.0",
        "django-tldap >= 0.2.9",
        "django-xmlrpc >= 0.1",
        "django_celery",
        "django_model_utils >= 2.0.0",
        "factory_boy",
        "matplotlib",
    ],
)
