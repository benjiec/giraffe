from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
  url(r'analyze/$', views.post, name='giraffe-analyze'),
  url(r'blast2/$', views.blast2, name='blast2')
)
