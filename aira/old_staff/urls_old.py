from django.conf.urls import patterns, url

from aira.views import (IndexPageView, HomePageView,
                        CreateProfile, UpdateProfile,
                        CreateAgrifield, UpdateAgrifield, AgrifieldDelete,
                        CreateCrop, UpdateCrop, DeleteCrop,
                        CreateLog, UpdateLog, DeleteLog)

urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(),
        name='welcome'),
#     url(r'^home/$', HomePageView.as_view(),
#         name='home'),
#     url(r'^/create_profile$', CreateProfile.as_view(),
#         name="create_profile"),
#     url(r'^/update_profile/(?P<pk>\d+)$', UpdateProfile.as_view(),
#         name="update_profile"),
#     url(r'^/add_agrifield/$', CreateAgrifield.as_view(),
#         name="add_agrifield"),
#     url(r'^/update_agrifield/(?P<pk>\d+)$', UpdateAgrifield.as_view(),
#         name="update_agrifield"),
#     url(r'^/delete_agrifield/(?P<pk>\d+)$', AgrifieldDelete.as_view(),
#         name="delete_agrifield"),
#     url(r'^/add_crop/(?P<pk>\d+)$', CreateCrop.as_view(), name="add_crop"),
#     url(r'^/update_crop/(?P<pk>\d+)$', UpdateCrop.as_view(),
#         name="update_crop"),
#     url(r'^/delete_crop/(?P<pk>\d+)$', DeleteCrop.as_view(),
#         name="delete_crop"),
#     url(r'^/add_log/(?P<pk>\d+)$', CreateLog.as_view(), name="add_log"),
#     url(r'^/update_log/(?P<pk>\d+)$', UpdateLog.as_view(),
#         name="update_log"),
#     url(r'^/delete_lop/(?P<pk>\d+)$', DeleteLog.as_view(),
#         name="delete_log")
)
