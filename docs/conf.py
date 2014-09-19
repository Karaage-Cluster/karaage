# Copyright 2007-2014 VPAC
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
from os.path import abspath, dirname, join

karaage_next_version = "3.1.5"

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
