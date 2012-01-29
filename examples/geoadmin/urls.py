from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse

from world.views import welcome
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', welcome),
)
    

urlpatterns += patterns('',
        (r'^media/(.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT, 'show_indexes': True})
    )