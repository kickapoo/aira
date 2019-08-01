try:
    from unittest import mock
except ImportError:
    import mock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from captcha.models import CaptchaStore
from model_mommy import mommy


@mock.patch(
    "aira.views.load_meteodata_file_paths",
    return_value=(
        ["temperature-2018-04-19.tif"],
        ["temperature-2018-04-19.tif"],
        ["temperature-2018-04-19.tif"],
        ["temperature-2018-04-19.tif"],
    ),
)
class TestIndexPageView(TestCase):
    def setUp(self):
        self.user = mommy.make(User, username="batman", is_active=True)
        # mommy.make is not hashing the password
        self.user.set_password("thegoatandthesheep")
        self.user.save()

    def test_index_view(self, mocked):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_registration_link_when_anonymous_on_index_view(self, mocked):
        resp = self.client.get("/")
        self.assertContains(resp, "Register")

    def test_no_registration_link_when_logged_on_index_view(self, mocked):
        resp = self.client.login(username="batman", password="thegoatandthesheep")
        self.assertTrue(resp)
        resp = self.client.get("/")
        self.assertTemplateUsed(resp, "aira/index.html")
        self.assertNotContains(resp, "Register")


class TestHomePageView(TestCase):
    def setUp(self):
        self.user = mommy.make(User, username="batman", is_active=True)
        # mommy.make is not hashing the password
        self.user.set_password("thegoatandthesheep")
        self.user.save()

    def test_home_view_denies_anynomous(self):
        resp = self.client.get("/home/", follow=True)
        self.assertRedirects(resp, "/accounts/login/?next=/home/")

    def test_home_view_loads_user(self):
        self.client.login(username="batman", password="thegoatandthesheep")
        resp = self.client.get("/home/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "aira/home.html")
