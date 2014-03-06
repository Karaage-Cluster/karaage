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

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os
import sys

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

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
code_dir = 'karaage'

for dirpath, dirnames, filenames in os.walk(code_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

with open('VERSION.txt', 'r') as f:
    version = f.readline().strip()

for dirpath, dirnames, filenames in os.walk('conf'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        data_files.append([dirpath.replace('conf', '/etc/karaage'), [os.path.join(dirpath, f) for f in filenames]])


data_files.append(
    ('/usr/sbin', ['sbin/kg_set_secret_key'])
)

setup(
    name = "karaage",
    version = version,
    url = 'http://code.vpac.org/trac/karaage/',
    author = 'Brian May',
    author_email = 'brian@vpac.org',
    description = 'Collection of Django apps to manage a clusters',
    packages = packages,
    data_files = data_files,
)
