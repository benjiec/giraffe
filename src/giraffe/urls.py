from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

urlpatterns = patterns('',
  (r'^demo/$', direct_to_template, { 'template' : 'giraffe/analyze.html' }),
  url(r'^$', views.post, name='blat-post'),
)

