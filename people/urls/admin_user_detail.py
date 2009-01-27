from django.conf.urls.defaults import *
from karaage.people.forms import UserForm

urlpatterns = patterns('karaage.people.views.admin_user_detail',

    url(r'^$', 'user_detail', name='kg_user_detail'),
    url(r'^activate/$', 'activate', name='admin_activate_user'),
    url(r'^jobs/$', 'user_job_list'), 
    url(r'^delete/$', 'delete_user', name='admin_delete_user'),
    url(r'^password_change/$', 'password_change'),
    url(r'^lock/$', 'lock_person'),
    url(r'^unlock/$', 'unlock_person'),
    url(r'^bounced_email/$', 'bounced_email'),
    url(r'^comments/$', 'user_comments', name='ac_user_comments'),
    url(r'^add_comment/$', 'add_comment', name='ac_user_add_comment'),

)

urlpatterns += patterns('karaage.people.views.admin',
    
    url(r'^add_useraccount/$', 'add_edit_useraccount'),
    url(r'^edit/$', 'add_edit_user', {'form_class': UserForm }),
)
