from django.contrib.auth.decorators import login_required
from django.urls import path

from aira import views

urlpatterns = [
    path("", views.IndexPageView.as_view(), name="welcome"),
    # Home
    path(
        "home/<str:username>/",
        login_required(views.HomePageView.as_view()),
        name="home",
    ),
    path("home/", login_required(views.HomePageView.as_view()), name="home"),
    # Advice
    path(
        "advice/<int:pk>/",
        login_required(views.AdvicePageView.as_view()),
        name="advice",
    ),
    # Profile
    path(
        "create_profile/",
        login_required(views.CreateProfile.as_view()),
        name="create_profile",
    ),
    path(
        "update_profile/<int:pk>/",
        login_required(views.UpdateProfile.as_view()),
        name="update_profile",
    ),
    path(
        "delete_profile/<int:pk>/",
        login_required(views.DeleteProfile.as_view()),
        name="delete_profile",
    ),
    # Agrifield
    path(
        "create_agrifield/<str:username>/",
        login_required(views.CreateAgrifield.as_view()),
        name="create_agrifield",
    ),
    path(
        "update_agrifield/<int:pk>/",
        login_required(views.UpdateAgrifield.as_view()),
        name="update_agrifield",
    ),
    path(
        "delete_agrifield/<int:pk>/",
        login_required(views.DeleteAgrifield.as_view()),
        name="delete_agrifield",
    ),
    path(
        "agrifield/<int:agrifield_id>/timeseries/<str:variable>/",
        login_required(views.AgrifieldTimeseries.as_view()),
        name="agrifield-timeseries",
    ),
    path(
        "agrifield/<int:agrifield_id>/soil_analysis/",
        login_required(views.DownloadSoilAnalysis.as_view()),
        name="agrifield-soil-analysis",
    ),
    # Irrigation Log
    path(
        "create_irrigationlog/<int:pk>/",
        login_required(views.CreateIrrigationLog.as_view()),
        name="create_irrlog",
    ),
    path(
        "update_irrigationlog/<int:pk_a>/<int:pk>/",
        login_required(views.UpdateIrrigationLog.as_view()),
        name="update_irrlog",
    ),
    path(
        "delete_irrigationlog/<int:pk_a>/<int:pk>/",
        login_required(views.DeleteIrrigationLog.as_view()),
        name="delete_irrlog",
    ),
    path(
        "conversion_tools/",
        login_required(views.ConversionTools.as_view()),
        name="tools",
    ),
    path("try/", views.TryPageView.as_view(), name="try"),
    path(
        "irrigation-performance-chart/<int:pk_a>/",
        views.IrrigationPerformance.as_view(),
        name="irrigation-chart",
    ),
    path(
        "download-irrigation-performance/<int:pk>/",
        views.performance_csv,
        name="performance_csv",
    ),
    path(
        "supervised_user/remove/",
        login_required(views.remove_supervised_user_from_user_list),
        name="supervised_user_remove",
    ),
]
