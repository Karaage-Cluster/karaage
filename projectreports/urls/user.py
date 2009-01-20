from django.conf.urls.defaults import *


urlpatterns = patterns('karaage.projectreports.views.user',

    url(r'^(?P<project_id>[-.\w]+)/$', 'survey', name='kg_survey'),
    url(r'^(?P<project_id>[-.\w]+)/thanks/$', 'thanks', name='kg_survey_thanks'),

)

                        
