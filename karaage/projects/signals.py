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
from django.dispatch import receiver
from karaage.people.emails import send_project_expired_email

from karaage.projects.models import Projects
from karaage.signals import daily_cleanup


@receiver(daily_cleanup)
def daily_cleanup(sender, **kwargs):
    for project in Projects.objects.filter(end_date__eq=datetime.datetime.today()):
        send_project_expired_email(project)
