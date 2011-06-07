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

PERIODS = [ 7, 90, 365 ]

def gen_all_project_graphs(period):
    from karaage.projects.models import Project
    from karaage.graphs import gen_project_graph
    import datetime
    project_list = Project.objects.all()

    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for p in project_list:
        for mc in p.machine_categories.all():
            gen_project_graph(p, start, end, mc)


class Command(BaseCommand):
    help = "Generates usage graphs"
    
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        for p in PERIODS:
            if verbose > 1:
                print "Generating project graphs for last %s days" % p
            gen_all_project_graphs(p)

