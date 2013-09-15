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
import django.db.transaction
import tldap.transaction


class Command(BaseCommand):
    help = "Regular cleanup of application db models."
    
    @django.db.transaction.commit_on_success
    @tldap.transaction.commit_on_success
    def handle(self, **options):
        from karaage.applications.models import Application, ProjectApplication, Applicant
        import datetime
        now = datetime.datetime.now()
        
        verbose = int(options.get('verbosity'))
        # Delete all expired applications
        for application in Application.objects.filter(expires__lte=now, state=Application.OPEN):
            if verbose >= 1:
                print "Deleted expired application #%s" % application.id
            application.delete()
 
        # Delete all project applications that have been complete for 1 month
        month_ago = now - datetime.timedelta(days=30)
        for application in ProjectApplication.objects.filter(state__in=[Application.COMPLETE, Application.DECLINED], complete_date__lte=month_ago):
            if verbose >= 1:
                print "Deleted completed project application #%s" % application.id
            application.delete()

        # Delete all orphaned applicants
        for applicant in Applicant.objects.filter(applications__isnull=True):
            if verbose >= 1:
                print "Deleted orphaned applicant #%s" % applicant.id
            application.delete()
