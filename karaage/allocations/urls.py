from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    'karaage.allocations.views',
    url(r'^allocation-period/(?P<allocationperiod_id>\d+)/$',
        'allocation_period', name='allocation_period'),
)
