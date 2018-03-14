from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from aira.forms import MyRegistrationForm
from registration.backends.default.views import RegistrationView

urlpatterns = patterns(
    '',
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=MyRegistrationForm),
        name='registration_register'),
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    #   http://stackoverflow.com/questions/19985103/
    url(r'^password/change/$', auth_views.password_change,
        name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset,
        name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'', include('aira.urls')),
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += patterns('django.contrib.flatpages.views',
                        url(r'^description/$', 'flatpage',
                            {'url': '/description/'}, name='description'),
                        url(r'^terms-of-use/$', 'flatpage',
                            {'url': '/terms-of-use/'}, name='terms'),
                        url(r'^disclaimer/$', 'flatpage',
                            {'url': '/disclaimer/'}, name='disclaimer'),
                        )
