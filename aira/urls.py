from django.conf.urls import patterns, url

from aira.views import (IndexPageView, HomePageView,
                        CreateProfile, UpdateProfile)

urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(), name='welcome'),
    url(r'^home/$',
        HomePageView.as_view(),
        name='home'),
    # Profile
    url(r'^/create_profile$',
        CreateProfile.as_view(),
        name="create_profile"),
    url(r'^/update_profile/(?P<pk>\d+)$',
        UpdateProfile.as_view(),
        name="update_profile"),
    # Agrifield
    # Irrigation Log
)
