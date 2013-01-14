from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf import settings

import django.contrib.admin
django.contrib.admin.autodiscover()

import views

urlpatterns = patterns('',
    url(r'^analyze/(\w+)/(\w+)/?$', 'hippo.demo_views.test_analyze', name='analyzer'),
    (r'^draw/(\w+)/(\w+)/?$', 'hippo.demo_views.test_draw'),
    (r'^/?$', direct_to_template, { 'template' : 'hippo/post.html' }),
)

