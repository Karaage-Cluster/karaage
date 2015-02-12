# Copyright 2015 VPAC
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
import os
import shutil

from ...dirs import GRAPH_ROOT


class Command(BaseCommand):
    help = "Deletes all usage graphs"

    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        if verbose > 1:
            print("Cleaning all graphs")

        for dirpath, dirnames, filenames in os.walk(GRAPH_ROOT):
            for name in dirnames:
                path = os.path.join(dirpath, name)
                if verbose > 1:
                    print("Cleaning %s" % path)
                shutil.rmtree(path)
            break
