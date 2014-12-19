from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


from aira.views import (IndexPageView, HomePageView,
                        CreateProfile, UpdateProfile,
                        CreateAgrifield, UpdateAgrifield, DeleteAgrifield,
                        CreateIrrigationLog, UpdateIrrigationLog,
                        DeleteIrrigationLog)

urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(), name='welcome'),
    url(r'^home/$',
        login_required(HomePageView.as_view()),
        name='home'),
    # Map per user_login
    url(r'^user_map/$',
        login_required(TemplateView.as_view(template_name='user_map.html')),
        name='user_map'),
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
    url(r'^create_timelog$',
        login_required(CreateIrrigationLog.as_view()),
        name="create_timelog"),
    url(r'^update_timelog/(?P<pk>\d+)/$',
        login_required(UpdateIrrigationLog.as_view()),
        name="update_timelog"),
    url(r'^delete_timelog/(?P<pk>\d+)/$',
        login_required(DeleteIrrigationLog.as_view()),
        name="delete_timelog"),
)
