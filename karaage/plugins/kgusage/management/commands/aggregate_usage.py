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

import datetime
import tldap.transaction

from django.core.management.base import BaseCommand
import django.db.transaction
from django.db.models import Sum, Count
from django.contrib.contenttypes.models import ContentType

from ...models import CPUJob
from karaage.common.models import Usage
from karaage.people.models import CareerLevel
from karaage.institutes.models import Institute
from karaage.projects.models import Project, ProjectLevel
from karaage.machines.models import ResourceFunction, ResourceUnits
from karaage.machines.models import Machine, Account, ResourcePool, Resource


class Command(BaseCommand):
    help = "Generates Aggregated Usage data"

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        # verbose = int(options.get('verbosity'))

        content_type = ContentType.objects.get_for_model(CPUJob)
        resource_pool, _ = ResourcePool.objects.get_or_create(
            content_type=content_type,
            defaults={
                'name': "CPU Hours",
                'description': "CPU Hours for Jobs run",
                'resource_function': ResourceFunction.SUM,
                'resource_units': ResourceUnits.CPU_HOURS,
            }
        )

        query = CPUJob.objects.all()
        query = query.values(
            'date',
            'account', 'machine', 'project',
            'person_institute', 'person_career_level',
            'person_project_level', 'project_institute',
        )
        query = query.annotate(usage=Sum('cpu_usage'), jobs=Count('id'))
        query = query.order_by()

        for row in query:
            print(row)

            if row['account'] is None:
                continue

            if row['project'] is None:
                continue

            range_start = row['date']
            range_end = range_start + datetime.timedelta(days=1)

            account = Account.objects.get(pk=row['account'])
            project = Project.objects.get(pk=row['project'])
            machine = Machine.objects.get(pk=row['machine'])

            person = account.person

            if row['person_institute'] is not None:
                person_institute = Institute.objects.get(
                    pk=row['person_institute'])
            else:
                person_institute = None

            if row['person_career_level'] is not None:
                person_career_level = CareerLevel.objects.get(
                    pk=row['person_career_level'])
            else:
                person_career_level = None

            if row['person_project_level'] is not None:
                person_project_level = ProjectLevel.objects.get(
                    pk=row['person_project_level'])
            else:
                person_project_level = None

            if row['project_institute'] is not None:
                project_institute = Institute.objects.get(
                    pk=row['project_institute'])
            else:
                project_institute = None

            resource, c = Resource.objects.get_or_create(
                machine=machine,
                resource_pool=resource_pool,
                defaults={
                    'scaling_factor': machine.scaling_factor,
                    'resource_name': None,
                    'quantity': None,
                }
            )
            used = row['usage'] * resource.scaling_factor

            # FIXME
            allocated_project = project
            allocation_pool = None
            allocation_period = None

            Usage.objects.update_or_create(
                range_start=range_start,
                range_end=range_end,
                account=account,
                machine=machine,
                submitted_project=project,
                person_institute=person_institute,
                person_career_level=person_career_level,
                person_project_level=person_project_level,
                project_institute=project_institute,

                defaults={
                    'person': person,
                    'count':  row['jobs'],
                    'raw_used':  row['usage'],
                    'used': used,

                    'resource':  resource,
                    'resource_pool':  resource_pool,

                    'allocated_project':  allocated_project,
                    'allocation_pool': allocation_pool,
                    'allocation_period': allocation_period,
                }
            )
