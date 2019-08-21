import os
import shutil
from tempfile import mkdtemp

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings

from model_mommy import mommy

from aira.models import Agrifield


class TestIndexPageView(TestCase):
    def setUp(self):
        self.tempdir = mkdtemp()
        self.settings_overrider = override_settings(AIRA_DATA_HISTORICAL=self.tempdir)
        self.settings_overrider.__enter__()
        open(os.path.join(self.tempdir, "daily_rain-2018-04-19.tif"), "w").close()
        self.user = mommy.make(User, username="batman", is_active=True)
        # mommy.make is not hashing the password
        self.user.set_password("thegoatandthesheep")
        self.user.save()

    def tearDown(self):
        self.settings_overrider.__exit__(None, None, None)
        shutil.rmtree(self.tempdir)

    def test_index_view(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_registration_link_when_anonymous_on_index_view(self):
        resp = self.client.get("/")
        self.assertContains(resp, "Register")

    def test_no_registration_link_when_logged_on_index_view(self):
        resp = self.client.login(username="batman", password="thegoatandthesheep")
        self.assertTrue(resp)
        resp = self.client.get("/")
        self.assertTemplateUsed(resp, "aira/index.html")
        self.assertNotContains(resp, "Register")

    def test_start_and_end_dates(self):
        response = self.client.get("/")
        self.assertContains(
            response,
            (
                'Time Period: <span class="text-success">2018-04-19</span> : '
                '<span class="text-success">2018-04-18</span>'
            ),
            html=True,
        )


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
        self.assertTemplateUsed(resp, "aira/home/main.html")


class AgrifieldEditViewTestCase(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="topsecret")
        self.agrifield = mommy.make(
            Agrifield, name="hello", location=Point(23, 38), owner=self.alice
        )

    def test_get(self):
        self.client.login(username="alice", password="topsecret")
        response = self.client.get("/update_agrifield/{}/".format(self.agrifield.id))
        self.assertContains(response, "hello")


class AgrifieldCreateTestCase(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="topsecret")
        self.client.login(username="alice", password="topsecret")
        self.response = self.client.get("/create_agrifield/alice/")

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)
