from django.conf.urls import patterns, url

from aira.views import IndexPageView

urlpatterns = patterns(
    '',
    url(r'^$', IndexPageView.as_view(), name='welcome'),
)
