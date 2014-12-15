from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    'karaage.allocations.views',
    url(r'^allocation-period/add/$',
        'allocation_period_add', name='allocation_period_add'),
    url(r'^add-allocation/$', 'allocation_add', name='allocation_add'),
    url(r'^add-grant/$', 'grant_add', name='grant_add'),
    url(r'^add-scheme/$', 'scheme_add', name='scheme_add'),
)
