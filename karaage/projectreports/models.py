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

from django.db import models

from django_surveys.models import Survey

from karaage.projects.models import Project


class ProjectSurvey(Survey):
    project = models.ForeignKey(Project)

    def __unicode__(self):
	return "%s - %s" % (self.survey_group, self.project.pid)

    @models.permalink
    def get_absolute_url(self):
        return ('kg_projectreport_detail', [self.id,])
