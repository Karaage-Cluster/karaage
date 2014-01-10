# Copyright 2007-2013 VPAC
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

from django.core.management.base import BaseCommand
from django.conf import settings
import os

GRAPH_BASE_DIR = settings.GRAPH_ROOT

class Command(BaseCommand):
    help = "Deletes all usage graphs"
    verbose = 0

    def _clean_resource(self, resource_type):

        if self.verbose > 1:
            print "Cleaning all %s graphs." % (resource_type.title())

        RESOURCE_DIR = os.path.join(GRAPH_BASE_DIR, resource_type, '')
        if not os.path.exists(RESOURCE_DIR):
            print "No %s graphs to clean." % (resource_type.title())
            return

        file_list = os.listdir(RESOURCE_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (RESOURCE_DIR,f))


    def handle(self, **options):
        self.verbose = int(options.get('verbosity'))

        self._clean_resource('projects')
        self._clean_resource('institutes')
        self._clean_resource('trends')
        self._clean_resource('i_trends')
