# Copyright 2010-2017, The University of Melbourne
# Copyright 2010-2017, Brian May
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
from karaage.people.emails import send_project_pending_expiration_email

from karaage.common import log
from karaage.projects.models import Project


def daily_cleanup():
    today = datetime.datetime.today()
    threshold = today + datetime.timedelta(days=30)

    Project.objects.filter(is_active=False, has_notified_pending_expiration=True).update(
        has_notified_pending_expiration=False
    )

    Project.objects.filter(end_date__isnull=True, has_notified_pending_expiration=True).update(
        has_notified_pending_expiration=False
    )

    Project.objects.filter(end_date__gt=threshold, has_notified_pending_expiration=True).update(
        has_notified_pending_expiration=False
    )

    for project in Project.objects.filter(end_date__lt=today, is_active=True):
        project.has_notified_pending_expiration = True
        project.deactivate()
        log.delete(project, "Project expired")

    for project in Project.objects.filter(
        end_date__lte=threshold, has_notified_pending_expiration=False, is_active=True
    ):
        send_project_pending_expiration_email(project)
        project.has_notified_pending_expiration = True
        project.save()
        log.delete(project, "Project renewal reminder sent")
