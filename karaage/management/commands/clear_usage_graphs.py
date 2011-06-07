# Copyright 2007-2010 VPAC
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
    
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        if verbose > 1:
            print "Cleaning all Project graphs"

        PROJECT_DIR = '%s/projects/' % GRAPH_BASE_DIR
        file_list = os.listdir(PROJECT_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (PROJECT_DIR,f))
            
        if verbose > 1:
            print "Cleaning all Institute graphs"

        INSTITUTE_DIR = '%s/institutes/' % GRAPH_BASE_DIR
        file_list = os.listdir(INSTITUTE_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (INSTITUTE_DIR,f))

        if verbose > 1:
            print "Cleaning all trend graphs"
        

        TRENDS_DIR = '%s/trends/' % GRAPH_BASE_DIR
        file_list = os.listdir(TRENDS_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (TRENDS_DIR,f))

        if verbose > 1:
            print "Cleaning all institute trend graphs"

        I_TRENDS_DIR = '%s/i_trends/' % GRAPH_BASE_DIR
        file_list = os.listdir(I_TRENDS_DIR)
        for f in file_list:
            if not f == '.svn':
                os.remove('%s%s' % (I_TRENDS_DIR,f))


