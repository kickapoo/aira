from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import RedirectView

from aira import views

urlpatterns = [
    path("", views.FrontPageView.as_view(), name="welcome"),
    # Home
    path(
        "home/<str:username>/",
        login_required(views.AgrifieldListView.as_view()),
        name="home",
    ),
    path("home/", login_required(views.AgrifieldListView.as_view()), name="home"),
    # Recommendation
    path(
        "advice/<int:pk>/",
        RedirectView.as_view(permanent=True, pattern_name="recommendation"),
    ),
    path(
        "recommendation/<int:pk>/",
        login_required(views.RecommendationView.as_view()),
        name="recommendation",
    ),
    # Profile
    path(
        "create_profile/",
        login_required(views.CreateProfileView.as_view()),
        name="create_profile",
    ),
    path(
        "update_profile/<int:pk>/",
        login_required(views.UpdateProfileView.as_view()),
        name="update_profile",
    ),
    path(
        "delete_profile/<int:pk>/",
        login_required(views.DeleteProfileView.as_view()),
        name="delete_profile",
    ),
    # Agrifield
    path(
        "create_agrifield/<str:username>/",
        login_required(views.CreateAgrifieldView.as_view()),
        name="create_agrifield",
    ),
    path(
        "update_agrifield/<int:pk>/",
        login_required(views.UpdateAgrifieldView.as_view()),
        name="update_agrifield",
    ),
    path(
        "delete_agrifield/<int:pk>/",
        login_required(views.DeleteAgrifieldView.as_view()),
        name="delete_agrifield",
    ),
    path(
        "agrifield/<int:agrifield_id>/timeseries/<str:variable>/",
        login_required(views.AgrifieldTimeseriesView.as_view()),
        name="agrifield-timeseries",
    ),
    path(
        "agrifield/<int:agrifield_id>/soil_analysis/",
        login_required(views.DownloadSoilAnalysisView.as_view()),
        name="agrifield-soil-analysis",
    ),
    path(
        "create_irrigationlog/<int:pk>/",
        login_required(views.CreateIrrigationLogView.as_view()),
        name="create_irrlog",
    ),
    path(
        "update_irrigationlog/<int:pk>/",
        login_required(views.UpdateIrrigationLogView.as_view()),
        name="update_irrlog",
    ),
    path(
        "delete_irrigationlog/<int:pk>/",
        login_required(views.DeleteIrrigationLogView.as_view()),
        name="delete_irrlog",
    ),
    path(
        "conversion_tools/",
        login_required(views.ConversionToolsView.as_view()),
        name="tools",
    ),
    path("try/", views.DemoView.as_view(), name="try"),
    path(
        "irrigation-performance-chart/<int:pk>/",
        views.IrrigationPerformanceView.as_view(),
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
