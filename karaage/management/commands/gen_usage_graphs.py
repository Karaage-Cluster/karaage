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

"""
Non-interactive command that generates all project graphs for last 7, 90,
and 365 days.
"""

from django.core.management.base import BaseCommand
import django.db.transaction
import tldap.transaction

PERIODS = [ 7, 90, 365 ]

def gen_all_project_graphs(period):
    """ Generate all project graph for list period days. """
    from karaage.machines.models import MachineCategory
    from karaage.projects.models import Project
    from karaage.graphs import gen_project_graph
    import datetime
    project_list = Project.objects.all()

    end = datetime.date.today()
    start = end - datetime.timedelta(days=period)

    for project in project_list:
        for machine_category in MachineCategory.objects.all():
            gen_project_graph(project, start, end, machine_category)


class Command(BaseCommand):
    """
    Non-interactive command that generates all project graphs for last 7, 90,
    and 365 days.
    """
    help = "Generates usage graphs"

    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        verbose = int(options.get('verbosity'))

        for p in PERIODS:
            if verbose > 1:
                print "Generating project graphs for last %s days" % p
            gen_all_project_graphs(p)

