from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

# from aira.views import edit_profile, home, index, user_map, \
#     update_fields, update_crop, update_irrigationlog, next_irrigation

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    #   http://stackoverflow.com/questions/19985103/
    url(r'^password/change/$', auth_views.password_change,
        name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset,
        name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    # url(r'^$', index, name="welcome"),
    # url(r'^home/$', home, name="home"),
    # url(r'^user_map/', user_map, name="user_map"),
    # url(r'^edit_profile', edit_profile, name="edit_profile"),
    # url(r'^update_fields', update_fields, name="update_fields"),
    # url(r'^update_crop/(?P<field_id>\d+)$', update_crop,
    #     name="update_crop"),
    # url(r'^update_irrigationlog/(?P<crop_id>\d+)$', update_irrigationlog,
    #     name="update_irrigationlog"),
    # url(r'^update_irrigationlog/(?P<field_id>\d+)/(?P<crop_id>\d+)$',
    #     next_irrigation, name="next_irrigation"),
)
