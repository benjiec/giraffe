from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf import settings

import django.contrib.admin
django.contrib.admin.autodiscover()

import views

urlpatterns = patterns('',
    url(r'^test/analyze/(\w+)/(\w+)/?$', demo_views.test_analyze, name='analyzer'),
    (r'^test/draw/(\w+)/(\w+)/?$', demo_views.test_draw),
    (r'^/test/$', direct_to_template, { 'template' : 'hippo/post.html' }),
    (r'^/?$', direct_to_template, { 'template' : 'hippo/post.html' }),
)

