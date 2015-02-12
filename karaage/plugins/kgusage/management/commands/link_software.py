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

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import datetime

from karaage.plugins.kgsoftware.models import SoftwareVersion, Software

from ...models import CPUJob, UsedModules


class Command(BaseCommand):

    help = ("Link used modules to jobs in the DB. "
            "Defaults to parsing all of yesterdays data")

    option_list = BaseCommand.option_list + (
        make_option('-a', '--all', action='store_true',
                    dest='all', default=False,
                    help='Report on all months.'),
        make_option('--start',
                    dest='start', default='',
                    help='Start date to process modules from'),
    )

    def handle(self, **options):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        process_all = options.get('all', False)
        start = options.get('start', False)
        verbose = int(options.get('verbosity'))
        ignored_modules = getattr(settings, 'SOFTWARE_IGNORED_MODULES', [])

        if process_all:
            used_modules = UsedModules.objects.all()
        elif start:
            try:
                year, month, day = start.split('-')
                start = datetime.date(int(year), int(month), int(day))
                used_modules = UsedModules.objects.filter(
                    date_added__gte=start)
            except ValueError:
                raise CommandError('Failed to parse start date. '
                                   'Format YYYY-MM-DD')
        else:
            used_modules = UsedModules.objects.filter(date_added=yesterday)

        for um in used_modules:
            try:
                job = CPUJob.objects.get(jobid=um.jobid)
            except CPUJob.DoesNotExist:
                continue
            modules = um.modules.strip().split(':')
            for module in modules:
                if module in ignored_modules:
                    continue
                try:
                    sv = SoftwareVersion.objects.get(module=module)
                except SoftwareVersion.DoesNotExist:
                    try:
                        package_name, version_name = module.split('/')
                    except ValueError:
                        # workaround a bug in Modules
                        try:
                            package_name, version_name = module.split('//')
                        except ValueError:
                            try:
                                print('Failed to create a new software '
                                      'software from module string '
                                      '%s' % module)
                            except UnicodeEncodeError:
                                pass
                            continue
                    software, created = Software.objects.get_or_create(
                        name=package_name)
                    if created and verbose > 0:
                        print("Created new Software software %s" % software)
                    sv, created = SoftwareVersion.objects.get_or_create(
                        software=software, version=version_name)
                    if created and verbose > 0:
                        print("Created new Software version %s" % sv)
                    sv.module = module
                    sv.save()
                if verbose > 1:
                    print("Adding %s to %s" % (sv, job.jobid))
                job.software.add(sv)
                sv.machines.add(job.machine)
                if not sv.last_used or job.date > sv.last_used:
                    sv.last_used = job.date
                    sv.save()

            um.delete()
