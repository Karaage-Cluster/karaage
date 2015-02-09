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

# Hack to allow compatability with versions of django-pipline before 1.4.0
#
# This file can be deleted entirely after backward compatability no longer
# required.

from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

try:
    # django-pipeline 1.4.0
    from pipeline.templatetags.pipeline import *  # NOQA

except ImportError:
    # django-pipeline << 1.4.0
    from django import template
    register = template.Library()

    import pipeline.templatetags.compressed

    register.tag('javascript', pipeline.templatetags.compressed.compressed_js)
    register.tag('stylesheet', pipeline.templatetags.compressed.compressed_css)
