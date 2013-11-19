from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
import views

urlpatterns = patterns('',
  url(r'analyze/$', views.post, name='giraffe-analyze'),
  url(r'blast2/$', views.blast2, name='blast2'),
  (r'^demo/$', TemplateView.as_view(template_name='giraffe/analyze.html')),
  (r'^demo/draw/$', TemplateView.as_view(template_name='giraffe/draw.html')),
)

