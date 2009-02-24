from django.conf.urls.defaults import *

urlpatterns = patterns('karaage.emails.views',
               
    url(r'^$', 'send_email', name='kg_emails_index'),

)
