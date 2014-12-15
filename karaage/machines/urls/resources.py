from django.conf.urls import patterns, url

urlpatterns = patterns(
    'karaage.machines.views.resources',
    url(r'^add/$', 'resource_add', name='resource_add'),
    url(r'^add-pool/$', 'resource_pool_add', name='resource_pool_add'),
)
