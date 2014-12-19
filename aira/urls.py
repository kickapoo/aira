from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


from aira.views import (IndexPageView, HomePageView,
                        CreateProfile, UpdateProfile,
                        CreateAgrifield)

urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(), name='welcome'),
    url(r'^home/$',
        HomePageView.as_view(),
        name='home'),
    # Map per user_login
    url(r'^user_map/$',
        login_required(TemplateView.as_view(template_name='user_map.html')),
        name='user_map'),
    # Profile
    url(r'^create_profile/$',
        CreateProfile.as_view(),
        name="create_profile"),
    url(r'^update_profile/(?P<pk>\d+)/$',
        UpdateProfile.as_view(),
        name="update_profile"),
    # Agrifield
    url(r'^create_agrifield$',
        CreateAgrifield.as_view(),
        name="create_agrifield"),
    # Irrigation Log
)
