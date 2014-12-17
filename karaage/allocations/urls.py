from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    'karaage.allocations.views',
    url(r'^allocation-period/add/$',
        'allocation_period_add', name='allocation_period_add'),
    url(r'^project-(?P<project_id>\d+)/add-allocation/$',
        'add_edit_allocation', name='allocation_add'),
    url(r'^project-(?P<project_id>\d+)/edit-allocation/(?P<allocation_id>\d+)/$',
        'add_edit_allocation', name='allocation_edit'),
    url(r'^project-(?P<project_id>\d+)/delete-allocation/(?P<allocation_id>\d+)/$',
        'delete_allocation', name='allocation_delete'),
    url(r'^project-(?P<project_id>\d+)/add-grant/$',
        'add_edit_grant', name='grant_add'),
    url(r'^project-(?P<project_id>\d+)/edit-grant/(?P<grant_id>\d+)/$',
        'add_edit_grant', name='grant_edit'),
    url(r'^project-(?P<project_id>\d+)/delete-grant/(?P<grant_id>\d+)/$',
        'delete_grant', name='grant_delete'),
    url(r'^add-scheme/$', 'scheme_add', name='scheme_add'),
)
