from django.conf.urls import patterns, include, url

from django.conf import settings
from tr069_site import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^itms/',              include('itms.urls')),
    
    url(r'^admin/',             include(admin.site.urls)),
    
    (r'^$',             views.login_view),
    (r'^login/$',       views.login_view),
    (r'^logout/$',      views.logout_view),
    (r'^user/manage/$', views.user_manage),
    (r'^server/manage/$', views.server_manage),
    
    #(r'^check/$',       views.check_username),
)

if settings.DEBUG is False:
    urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
    # (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'}),
    # (r'^media/(?P<path>.*)','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
    