from django.conf.urls import patterns, include, url
from django.contrib import admin

import map.views
import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sonicmap.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r"^account/", include("account.urls")),
    
    url(r"^$", 'map.views.index', name='home'),
    url(r"^user/(?P<usr>\d+)/$", 'map.views.user_map', name='user_map'),
    url(r"^map/(?P<usr>\d+)/$", 'map.views.view_user_map', name='view_user_map'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^userpage/', 'map.views.user_redr', name='user_redr'),
    url(r'^zone/(?P<pk>\d+)/$', map.views.ZoneView.as_view(), name='zoneview'),
    url(r"^all/", 'map.views.view_all_map', name='view_all_map'),

    url(r'^all-json/', 'map.views.get_zone_json', name='json'),
    url(r'^json/(?P<usrid>\d+)/$', 'map.views.get_zone_json_user', name='json_user'),
    url(r'^json-send/', 'map.views.send_zone_json', name='send_json'),
    url(r'^all-zones/', 'map.views.view_all_zones_list', name='view_all_zones_list'),
    url(r'^zones/(?P<usr>\d+)/$', 'map.views.view_user_zones_list', name='view_user_zones_list'),

    url(r'^delete/zone/(?P<number>\d+)/$', 'map.views.delete_zone', name='delete_zone'),

    url(r'^tag-form/', 'map.views.tag_form', name='tag_form'),
    url(r'^delete/tag/(?P<number>\d+)/$', 'map.views.delete_tag', name='delete_tag'),

    url(r'^location/(?P<a>.+)/(?P<b>.+)/(?P<c>.+)$', r'map.views.location_session_data', name="send_location"),

    url(r'^all-bike-json/', 'map.views.get_bike_json', name='bike-json'),
    url(r'^bike-json/(?P<user>\d+)/$', 'map.views.get_bike_json_user', name='bike-json-user'),

)

urlpatterns += patterns('',
       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

