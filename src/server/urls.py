from django.conf.urls import patterns, include, url
from django.conf import settings

import django.contrib.admin
django.contrib.admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(django.contrib.admin.site.urls)),
    (r'^giraffe/', include('giraffe.urls')),
)

