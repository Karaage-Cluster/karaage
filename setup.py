#!/usr/bin/env python

# Copyright 2012-2014 VPAC
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

from setuptools import setup
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
for dirpath, dirnames, filenames in os.walk("kgusage"):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if filenames:
        packages.append('.'.join(fullsplit(dirpath)))

setup(
    name="karaage-usage",
    version=version,
    url='https://github.com/Karaage-Cluster/karaage',
    author='Brian May',
    author_email='brian@v3.org.au',
    description='Usage information for Karaage',
    packages=packages,
    license="GPL3+",
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 "
            "or later (GPLv3+)",
        "Operating System :: OS Independent"
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords="karaage cluster user administration",
    package_data={
        '': ['*.css', '*.html', '*.js', '*.png', '*.gif', '*.map', '*.txt'],
    },
    install_requires=[
        "django_celery",
        "django-filter",
        "django-tables2",
        "django-xmlrpc >= 0.1",
        "karaage >= 3.1.0",
        "karaage-software",
        "matplotlib",
    ],
)
