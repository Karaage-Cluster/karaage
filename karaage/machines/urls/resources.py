from django.conf.urls import patterns, url

urlpatterns = patterns(
    'karaage.machines.views.resources',
    url(r'^add-resource/$', 'add_edit_resource', name='resource_add'),
    url(r'^edit-resource/(?P<resource_id>\d+)/$',
        'add_edit_resource', name='resource_edit'),
    url(r'^delete-resource/(?P<resource_id>\d+)/$',
        'delete_resource', name='resource_delete'),
    url(r'^add-resource-pool/$',
        'add_edit_resource_pool', name='resource_pool_add'),
    url(r'^edit-resource-pool/(?P<resource_pool_id>\d+)/$',
        'add_edit_resource_pool', name='resource_pool_edit'),
    url(r'^delete-resource-pool/(?P<resource_pool_id>\d+)/$',
        'delete_resource_pool', name='resource_pool_delete'),
)
