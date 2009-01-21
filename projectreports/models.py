from django.db import models

from django_surveys.models import Survey

from karaage.projects.models import Project


class ProjectSurvey(Survey):
    project = models.ForeignKey(Project)


    @models.permalink
    def get_absolute_url(self):
        return ('kg_projectreport_detail', [self.id,])
