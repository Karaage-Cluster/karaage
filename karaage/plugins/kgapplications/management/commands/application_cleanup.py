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
import django.db.transaction
import tldap.transaction


class Command(BaseCommand):
    help = "Regular cleanup of application db models."

    @django.db.transaction.atomic
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        from django.db.models import Count
        from ...models import Application, Applicant
        import datetime
        now = datetime.datetime.now()

        verbose = int(options.get('verbosity'))

        # Delete all expired unsubmitted applications
        for application in Application.objects.filter(
                expires__lte=now, submitted_date__isnull=True):
            if verbose >= 1:
                print(
                    "Deleted expired unsubmitted application #%s"
                    % application.id)
            application.delete()

        month_ago = now - datetime.timedelta(days=30)

        # Delete all unsubmitted applications that have been around for 1 month
        for application in Application.objects.filter(
                created_date__lte=month_ago, submitted_date__isnull=True):
            if verbose >= 1:
                print("Deleted unsubmitted application #%s" % application.id)
            application.delete()

        # Delete all applications that have been complete/declined for 1 month
        for application in Application.objects.filter(
                complete_date__isnull=False, complete_date__lte=month_ago):
            if verbose >= 1:
                print("Deleted completed application #%s" % application.id)
            application.delete()

        # Delete all orphaned applicants
        for applicant in Applicant.objects.annotate(
                cc=Count('applications')).filter(cc=0):
            if verbose >= 1:
                print("Deleted orphaned applicant #%s" % applicant.id)
            applicant.delete()
