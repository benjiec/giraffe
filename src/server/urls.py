from django.conf.urls.defaults import *
from django.conf import settings

import django.contrib.admin
django.contrib.admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(django.contrib.admin.site.urls)),
    (r'^hippo/', include('hippo.urls')),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
      'document_root': settings.MEDIA_ROOT,
    }),
  )

