from django.urls import path
from django.contrib.auth.decorators import login_required


from aira.views import (
    IndexPageView,
    HomePageView,
    AdvicePageView,
    CreateProfile,
    UpdateProfile,
    DeleteProfile,
    CreateAgrifield,
    UpdateAgrifield,
    DeleteAgrifield,
    CreateIrrigationLog,
    UpdateIrrigationLog,
    DeleteIrrigationLog,
    TryPageView,
    ConversionTools,
    IrrigationPerformance,
    performance_csv,
    remove_supervised_user_from_user_list,
)

urlpatterns = [
    path("", IndexPageView.as_view(), name="welcome"),
    # Home
    path("home/<str:username>/", login_required(HomePageView.as_view()), name="home"),
    path("home/", login_required(HomePageView.as_view()), name="home"),
    # Advice
    path("advice/<int:pk>/", login_required(AdvicePageView.as_view()), name="advice"),
    # Profile
    path(
        "create_profile/",
        login_required(CreateProfile.as_view()),
        name="create_profile",
    ),
    path(
        "update_profile/<int:pk>/",
        login_required(UpdateProfile.as_view()),
        name="update_profile",
    ),
    path(
        "delete_profile/<int:pk>/",
        login_required(DeleteProfile.as_view()),
        name="delete_profile",
    ),
    # Agrifield
    path(
        "create_agrifield/<str:username>/",
        login_required(CreateAgrifield.as_view()),
        name="create_agrifield",
    ),
    path(
        "update_agrifield/<int:pk>/",
        login_required(UpdateAgrifield.as_view()),
        name="update_agrifield",
    ),
    path(
        "delete_agrifield/<int:pk>/",
        login_required(DeleteAgrifield.as_view()),
        name="delete_agrifield",
    ),
    # Irrigation Log
    path(
        "create_irrigationlog/<int:pk>/",
        login_required(CreateIrrigationLog.as_view()),
        name="create_irrlog",
    ),
    path(
        "update_irrigationlog/<int:pk_a>/<int:pk>/",
        login_required(UpdateIrrigationLog.as_view()),
        name="update_irrlog",
    ),
    path(
        "delete_irrigationlog/<int:pk_a>/<int:pk>/",
        login_required(DeleteIrrigationLog.as_view()),
        name="delete_irrlog",
    ),
    path("conversion_tools/", login_required(ConversionTools.as_view()), name="tools"),
    path("try/", TryPageView.as_view(), name="try"),
    path(
        "irrigation-performance-chart/<int:pk_a>/",
        IrrigationPerformance.as_view(),
        name="irrigation-chart",
    ),
    path(
        "download-irrigation-performance/<int:pk>/",
        performance_csv,
        name="performance_csv",
    ),
    path(
        "supervised_user/remove/",
        login_required(remove_supervised_user_from_user_list),
        name="supervised_user_remove",
    ),
]
