from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from aira.views import (IndexPageView, HomePageView,
                        UpdateProfile, CreateAgrifield,
                        UpdateAgrifield, CreateIrrigationLog)
from aira import ajax_views


urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(), name='welcome'),
    # Home
    url(r'^home/$',
        login_required(HomePageView.as_view()),
        name='home'),
    url(r'^home/(?P<username>[\w.@+-]+)/$',
        login_required(HomePageView.as_view()),
        name='home-username'),
    # Profile
    url(r'^profile/(?P<farmer>[-\w]+)$',
        login_required(UpdateProfile.as_view()),
        name="profile"),
    url(r'^profile/delete/account/$',
        login_required(ajax_views.delete_account),
        name='delete_account'),
    url(r'^profile/set/password/$',
        login_required(ajax_views.set_password),
        name='set_password'),
    url(r'^add-agrifield/(?P<username>[\w.@+-]+)/$',
        login_required(CreateAgrifield.as_view()),
        name="add-agrifield"),
    url(r'^edit-agrifield/(?P<username>[\w.@+-]+)/(?P<slug>[-\w]+)$',
        login_required(UpdateAgrifield.as_view()),
        name="edit-agrifield"),
    url(r'^delete/agrifield/$',
        login_required(ajax_views.delete_agrifield),
        name="delete_agrifield"),
    url(r'^add-irrigationlog-agrifield/(?P<slug>[\w.@+-]+)/$',
        login_required(CreateIrrigationLog.as_view()),
        name="add-irrigationlog"),

)
