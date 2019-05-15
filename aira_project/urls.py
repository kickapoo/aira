from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.flatpages.views import flatpage
from aira.forms import MyRegistrationForm
from registration.backends.default.views import RegistrationView

urlpatterns = [
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=MyRegistrationForm),
        name='registration_register'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('aira.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^description/$', flatpage, {'url': '/description/'}, name='description'),
    url(r'^terms-of-use/$', flatpage, {'url': '/terms-of-use/'}, name='terms'),
    url(r'^disclaimer/$', flatpage, {'url': '/disclaimer/'}, name='disclaimer'),
]
