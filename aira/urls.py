from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


from aira.views import (IndexPageView, HomePageView, AdvicePageView,
                        CreateProfile, UpdateProfile,
                        CreateAgrifield, UpdateAgrifield, DeleteAgrifield,
                        CreateIrrigationLog, UpdateIrrigationLog,
                        DeleteIrrigationLog)

urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(), name='welcome'),
    # Home
    url(r'^home/$',
        login_required(HomePageView.as_view()),
        name='home'),
    # Advice
    url(r'^advice/(?P<pk>\d+)/$',
        login_required(AdvicePageView.as_view()),
        name='advice'),
    # Profile
    url(r'^create_profile/$',
        login_required(CreateProfile.as_view()),
        name="create_profile"),
    url(r'^update_profile/(?P<pk>\d+)/$',
        login_required(UpdateProfile.as_view()),
        name="update_profile"),
    # Agrifield
    url(r'^create_agrifield$',
        login_required(CreateAgrifield.as_view()),
        name="create_agrifield"),
    url(r'^update_agrifield/(?P<pk>\d+)/$',
        login_required(UpdateAgrifield.as_view()),
        name="update_agrifield"),
    url(r'^delete_agrifield/(?P<pk>\d+)/$',
        login_required(DeleteAgrifield.as_view()),
        name="delete_agrifield"),
    # Irrigation Log
    url(r'^create_irrigationlog/(?P<pk>\d+)/$',
        login_required(CreateIrrigationLog.as_view()),
        name="create_irrlog"),
    url(r'^update_irrigationlog/(?P<pk>\d+)/$',
        login_required(UpdateIrrigationLog.as_view()),
        name="update_irrlog"),
    url(r'^delete_irrigationlog/(?P<pk>\d+)/$',
        login_required(DeleteIrrigationLog.as_view()),
        name="delete_irrlog"),
)
