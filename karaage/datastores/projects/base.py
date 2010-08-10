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

from django.contrib.auth.models import User
from django.conf import settings

import datetime
from andsome.middleware.threadlocals import get_current_user

from karaage.projects.models import Project
from karaage.projects.utils import get_new_pid
from karaage.util import log_object as log

class ProjectDataStore(object):


    def create_new_project(self, data):
        project = Project(
            pid=get_new_pid(data['project_institute']),
            name=data['project_name'],
            description=data['project_description'],
            institute=data['project_institute'],
            is_approved=False,
            is_active=False,
            is_expertise=False,
            additional_req=data['additional_req'],
            start_date=datetime.datetime.today(),
            end_date=datetime.datetime.today() + datetime.timedelta(days=365),
            )
        

        return project

    def activate_project(self, project):
        project.is_active = True
        project.is_approved = True
        project.date_approved = datetime.datetime.today()
        approver = get_current_user()
        project.approved_by = approver.get_profile()
        project.save()

        return project

    def deactivate_project(self, project):
        project.is_active = False
        deletor = get_current_user()    
        project.deleted_by = deletor.get_profile()
        project.date_deleted = datetime.datetime.today()    
        project.save()
        
        from karaage.datastores.projects import remove_user_from_project
        for user in project.users.all():
            remove_user_from_project(user, project)
        

    def add_user_to_project(self, person, project):
        from karaage.datastores import create_account

        project.users.add(person)
    
        for mc in project.machine_categories.all():
            if not person.has_account(mc):
                create_account(person, project, mc)


    def remove_user_from_project(self, person, project):
   
        project.users.remove(person)
