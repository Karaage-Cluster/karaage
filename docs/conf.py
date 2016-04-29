# Copyright 2014-2015 VPAC
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
import sys
import re
from os.path import abspath, dirname, join
from setuptools_scm import get_version


sys.path.append(abspath(join(dirname(dirname(__file__)), "ext")))

html_translator_class = "djangodocs.KaraageHTMLTranslator"

extensions = []
extensions += ['sphinx.ext.todo']
extensions += ["djangodocs"]
extensions += ["sphinx.ext.intersphinx"]
intersphinx_mapping = {
    'django': (
        'https://docs.djangoproject.com/en/1.7/',
        'https://docs.djangoproject.com/en/1.7/_objects/'),
}

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#

# The short X.Y version.
version = get_version(root="../..")
# The full version, including alpha/beta/rc tags.
release = version


def guess_next_version(tag_version):
    version = str(tag_version)
    if '.dev' in version:
        version, tail = version.rsplit('.dev', 1)

    prefix, tail = re.match('(.*?)(\d+)$', version).groups()
    return '%s%d' % (prefix, int(tail) + 1)

karaage_next_version = guess_next_version(version)
