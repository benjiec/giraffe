from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

urlpatterns = patterns('',
  url(r'analyze/$', views.post, name='giraffe-analyze'),
  (r'^demo/$', direct_to_template, { 'template' : 'giraffe/analyze.html' }),
  (r'^demo/draw/$', direct_to_template, { 'template' : 'giraffe/draw.html' }),
)

