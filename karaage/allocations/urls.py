from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    'karaage.allocations.views',
    url(r'^allocation-period/add/$',
        'allocation_period_add', name='allocation_period_add'),
)
