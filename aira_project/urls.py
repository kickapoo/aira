from django.urls import include, path
from django.contrib import admin
from django.contrib.flatpages.views import flatpage

from registration.backends.default.views import RegistrationView

from aira.forms import MyRegistrationForm


urlpatterns = [
    path(
        "accounts/register/",
        RegistrationView.as_view(form_class=MyRegistrationForm),
        name="registration_register",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("accounts/", include("registration.backends.default.urls")),
    path("", include("aira.urls")),
    path("captcha/", include("captcha.urls")),
    path("description/", flatpage, {"url": "/description/"}, name="description"),
    path("terms-of-use/", flatpage, {"url": "/terms-of-use/"}, name="terms"),
    path("disclaimer/", flatpage, {"url": "/disclaimer/"}, name="disclaimer"),
]
