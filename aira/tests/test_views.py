import os
import shutil
import tempfile
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

import numpy as np
from hspatial.test import setup_test_raster
from model_mommy import mommy

from aira.models import Agrifield
from aira.tests import RandomMediaRootMixin


class TestDataMixin:
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.mkdtemp()
        self.settings_overrider = override_settings(
            AIRA_COEFFS_RASTERS_DIR=self.tempdir
        )
        self.settings_overrider.__enter__()
        self._create_rasters()

    def tearDown(self):
        self.settings_overrider.__exit__(None, None, None)
        shutil.rmtree(self.tempdir)

    def _create_rasters(self):
        self._create_fc()
        self._create_pwp()
        self._create_theta_s()

    def _create_fc(self):
        setup_test_raster(
            os.path.join(self.tempdir, "fc.tif"),
            np.array([[0.20, 0.23, 0.26], [0.29, 0.32, 0.35], [0.38, 0.41, 0.44]]),
        )

    def _create_pwp(self):
        setup_test_raster(
            os.path.join(self.tempdir, "pwp.tif"),
            np.array([[0.06, 0.07, 0.08], [0.09, 0.10, 0.11], [0.12, 0.13, 0.14]]),
        )

    def _create_theta_s(self):
        setup_test_raster(
            os.path.join(self.tempdir, "theta_s.tif"),
            np.array([[0.38, 0.39, 0.40], [0.41, 0.42, 0.43], [0.44, 0.45, 0.46]]),
        )


class TestIndexPageView(TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
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


class AgrifieldEditViewTestCase(TestDataMixin, TestCase):
    def setUp(self):
        super().setUp()
        self._create_data()
        self._make_request()

    def _create_data(self):
        self.alice = User.objects.create_user(username="alice", password="topsecret")
        self.agrifield = mommy.make(
            Agrifield,
            name="hello",
            location=Point(22.01, 37.99),
            owner=self.alice,
            irrigation_type__efficiency=0.85,
            crop_type__max_allow_depletion=0.40,
            crop_type__root_depth_max=0.50,
            crop_type__root_depth_min=0.30,
        )

    def _make_request(self):
        self.client.login(username="alice", password="topsecret")
        self.response = self.client.get(
            "/update_agrifield/{}/".format(self.agrifield.id)
        )

    def test_response_contains_agrifield_name(self):
        self.assertContains(self.response, "hello")

    def test_default_irrigation_efficiency(self):
        self.assertContains(
            self.response,
            '<span id="default-irrigation-efficiency">0.85</span>',
            html=True,
        )

    def test_default_max_allow_depletion(self):
        self.assertContains(
            self.response,
            '<span id="default-max_allow_depletion">0.40</span>',
            html=True,
        )

    def test_default_root_depth_max(self):
        self.assertContains(
            self.response, '<span id="default-root_depth_max">0.5</span>', html=True
        )

    def test_default_root_depth_min(self):
        self.assertContains(
            self.response, '<span id="default-root_depth_min">0.3</span>', html=True
        )

    def test_default_irrigation_optimizer(self):
        self.assertContains(
            self.response,
            '<span id="default-irrigation-optimizer">0.5</span>',
            html=True,
        )

    def test_default_field_capacity(self):
        self.assertContains(
            self.response, '<span id="default-field-capacity">0.32</span>', html=True
        )

    def test_default_wilting_point(self):
        self.assertContains(
            self.response, '<span id="default-wilting-point">0.10</span>', html=True
        )

    def test_default_theta_s(self):
        self.assertContains(
            self.response, '<span id="default-theta_s">0.42</span>', html=True
        )


class AgrifieldCreateTestCase(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="topsecret")
        self.client.login(username="alice", password="topsecret")
        self.response = self.client.get("/create_agrifield/alice/")

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)


class AgrifieldWeatherHistoryTestCase(TestCase):
    def setUp(self):
        self._create_stuff()
        self._login()
        self._get_response()

    def _create_stuff(self):
        self._create_tempdir()
        self._override_settings()
        self._create_user()
        self._create_agrifield()
        self._create_dummy_result_file()

    def _create_tempdir(self):
        self.tempdir = tempfile.mkdtemp()

    def _override_settings(self):
        self.settings_overrider = override_settings(
            AIRA_TIMESERIES_CACHE_DIR=self.tempdir
        )
        self.settings_overrider.__enter__()

    def _create_dummy_result_file(self):
        self.dummy_result_pathname = os.path.join(
            settings.AIRA_TIMESERIES_CACHE_DIR,
            "agrifield{}-temperature.hts".format(self.agrifield.id),
        )
        with open(self.dummy_result_pathname, "w") as f:
            f.write("These are the dummy result file contents")

    def _create_user(self):
        self.alice = User.objects.create_user(username="alice", password="topsecret")

    def _create_agrifield(self):
        self.agrifield = mommy.make(
            Agrifield, name="hello", location=Point(23, 38), owner=self.alice
        )

    def _login(self):
        self.client.login(username="alice", password="topsecret")

    def _get_response(self):
        patcher = patch(
            "aira.views.PointTimeseries",
            **{"return_value.get_cached.return_value": self.dummy_result_pathname},
        )
        with patcher as m:
            self.mock_point_timeseries = m
            self.response = self.client.get(
                "/agrifield/{}/timeseries/temperature/".format(self.agrifield.id)
            )

    def tearDown(self):
        self.settings_overrider.__exit__(None, None, None)
        shutil.rmtree(self.tempdir)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_response_contents(self):
        content = b""
        for chunk in self.response.streaming_content:
            content += chunk
        self.assertEqual(content, b"These are the dummy result file contents")

    def test_called_point_timeseries(self):
        self.mock_point_timeseries.assert_called_once_with(
            point=self.agrifield.location,
            prefix=os.path.join(settings.AIRA_DATA_HISTORICAL, "daily_temperature"),
        )

    def test_called_get_cached(self):
        self.mock_point_timeseries.return_value.get_cached.assert_called_once_with(
            self.dummy_result_pathname, version=2
        )


class DownloadSoilAnalysisTestCase(TestCase, RandomMediaRootMixin):
    def setUp(self):
        self.override_media_root()
        self.alice = User.objects.create_user(username="alice", password="topsecret")
        self.agrifield = mommy.make(Agrifield, id=1, owner=self.alice)
        self.agrifield.soil_analysis.save("somefile", ContentFile("hello world"))
        self.client.login(username="alice", password="topsecret")
        self.response = self.client.get("/agrifield/1/soil_analysis/")

    def tearDown(self):
        self.end_media_root_override()

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_content(self):
        content = b""
        for x in self.response.streaming_content:
            content += x
        self.assertEqual(content, b"hello world")
