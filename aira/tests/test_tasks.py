import datetime as dt
import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings

import numpy as np
from freezegun import freeze_time
from model_mommy import mommy
from osgeo import gdal, osr

from aira.models import Agrifield, CropType, IrrigationLog, IrrigationType
from aira.tasks import calculate_performance_chart, execute_model


def setup_input_file(filename, value, timestamp):
    """Save value, which is an np array, to a GeoTIFF file."""
    nodata = 1e8
    value[np.isnan(value)] = nodata
    f = gdal.GetDriverByName("GTiff").Create(filename, 2, 2, 1, gdal.GDT_Float32)
    try:
        timestamp = timestamp or dt.datetime(1970, 1, 1)
        f.SetMetadataItem("TIMESTAMP", timestamp.isoformat())
        f.SetGeoTransform((22.0, 0.01, 0, 38.0, 0, -0.01))
        wgs84 = osr.SpatialReference()
        wgs84.ImportFromEPSG(4326)
        f.SetProjection(wgs84.ExportToWkt())
        f.GetRasterBand(1).SetNoDataValue(nodata)
        f.GetRasterBand(1).WriteArray(value)
    finally:
        f = None


class SetupTestDataMixin:
    def _setup_test_data(self):
        self._setup_field_capacity_raster()
        self._setup_draintime_rasters()
        self._setup_theta_s_raster()
        self._setup_pwp_raster()
        self._setup_meteo_rasters()
        self._setup_agrifield()

    def _setup_field_capacity_raster(self):
        filename = os.path.join(self.tempdir, "fc.tif")
        setup_input_file(filename, np.array([[1, 1], [1, 1]]), None)

    def _setup_draintime_rasters(self):
        filename = os.path.join(self.tempdir, "a_1d.tif")
        setup_input_file(filename, np.array([[30, 30], [30, 30]]), None)
        filename = os.path.join(self.tempdir, "b.tif")
        setup_input_file(filename, np.array([[0.95, 0.95], [0.95, 0.95]]), None)

    def _setup_theta_s_raster(self):
        filename = os.path.join(self.tempdir, "theta_s.tif")
        setup_input_file(filename, np.array([[0.5, 0.5], [0.5, 0.5]]), None)

    def _setup_pwp_raster(self):
        filename = os.path.join(self.tempdir, "pwp.tif")
        setup_input_file(filename, np.array([[0.1, 0.1], [0.1, 0.1]]), None)

    def _setup_meteo_rasters(self):
        self._setup_test_raster("rain", "2018-03-15", [[0.0, 0.1], [0.2, 0.3]])
        self._setup_test_raster("evaporation", "2018-03-15", [[2.1, 2.2], [2.3, 2.4]])
        self._setup_test_raster("rain", "2018-03-16", [[0.5, 0.6], [0.7, 0.8]])
        self._setup_test_raster("evaporation", "2018-03-16", [[9.1, 9.2], [9.3, 9.4]])
        self._setup_test_raster("rain", "2018-03-17", [[0.4, 0.5], [0.6, 0.7]])
        self._setup_test_raster("evaporation", "2018-03-17", [[9.5, 9.6], [9.7, 9.8]])
        self._setup_test_raster("rain", "2018-03-18", [[0.3, 0.2], [0.1, 0.0]])
        self._setup_test_raster("evaporation", "2018-03-18", [[9.6, 9.7], [9.8, 9.9]])

    def _setup_test_raster(self, var, datestr, contents):
        subdir = "forecast" if datestr >= "2018-03-18" else "historical"
        filename = os.path.join(
            self.tempdir, subdir, "daily_{}-{}.tif".format(var, datestr)
        )
        year, month, day = [int(x) for x in datestr.split("-")]
        timestamp = dt.datetime(year, month, day)
        setup_input_file(filename, np.array(contents), timestamp)

    def _setup_agrifield(self):
        self.crop_type = mommy.make(
            CropType,
            name="Grass",
            root_depth_max=0.7,
            root_depth_min=1.2,
            max_allow_depletion=0.5,
            fek_category=4,
            kc_init=0.7,
            kc_mid=0.7,
            kc_end=0.7,
            days_kc_init=10,
            days_kc_dev=20,
            days_kc_mid=20,
            days_kc_late=30,
            planting_date=dt.date(2018, 3, 16),
        )
        self.irrigation_type = mommy.make(
            IrrigationType, name="Surface irrigation", efficiency=0.60
        )
        self.user = mommy.make(User, username="batman", is_active=True)
        self.agrifield = mommy.make(
            Agrifield,
            owner=self.user,
            name="A field",
            crop_type=self.crop_type,
            irrigation_type=self.irrigation_type,
            latitude=38.00,
            longitude=22.00,
            area=2000,
        )
        self.irrigation_log = mommy.make(
            IrrigationLog,
            agrifield=self.agrifield,
            time=dt.datetime(2018, 3, 15, 7, 0, tzinfo=dt.timezone.utc),
            applied_water=500,
        )


@freeze_time("2018-03-18 13:00:01")
class ExecuteModelTestCase(TestCase, SetupTestDataMixin):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.tempdir, "historical"))
        os.mkdir(os.path.join(self.tempdir, "forecast"))
        self._setup_test_data()
        h = override_settings(
            AIRA_DATA_HISTORICAL=os.path.join(self.tempdir, "historical")
        )
        f = override_settings(AIRA_DATA_FORECAST=os.path.join(self.tempdir, "forecast"))
        r = override_settings(AIRA_COEFFS_RASTERS_DIR=self.tempdir)
        d = override_settings(AIRA_DRAINTIME_DIR=self.tempdir)
        with h, f, r, d:
            self.results = execute_model(self.agrifield)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_results(self):
        self.assertEqual(len(self.results.__dict__), 10)
        self.assertTrue(self.results.adv)
        self.assertEqual(self.results.adv_sorted[0][0], dt.date(2018, 3, 18))
        self.assertAlmostEqual(self.results.adv_sorted[0][1], 0.8668036)
        self.assertAlmostEqual(self.results.adv_sorted[0][2], 407.3845070)
        self.assertAlmostEqual(self.results.adv_sorted[0][3], 814.7690140)
        self.assertEqual(self.results.ed, dt.date(2018, 3, 17))
        self.assertEqual(self.results.edh, dt.date(2018, 3, 18))
        self.assertAlmostEqual(self.results.ifinal, 407.3845070)
        self.assertAlmostEqual(self.results.ifinal_m3, 814.7690140)
        self.assertEqual(self.results.sd, dt.date(2018, 3, 15))
        self.assertEqual(self.results.sdh, dt.date(2018, 3, 18))
        self.assertEqual(self.results.swb_report[0][0], dt.date(2018, 3, 18))
        self.assertAlmostEqual(self.results.swb_report[0][1], 0.24)
        self.assertAlmostEqual(self.results.swb_report[0][2], 488.8614084)
        self.assertAlmostEqual(self.results.swb_report[0][3], 0.4854090)
        self.assertTrue(self.results.swb_report[0][4])
        self.assertAlmostEqual(self.results.swb_report[0][5], 0.8668036)
        self.assertAlmostEqual(self.results.swb_report[0][6], 407.3845070)


@freeze_time("2018-03-18 13:00:01")
class CalculatePerformanceChartTestCase(TestCase, SetupTestDataMixin):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.tempdir, "historical"))
        os.mkdir(os.path.join(self.tempdir, "forecast"))
        self._setup_test_data()
        h = override_settings(
            AIRA_DATA_HISTORICAL=os.path.join(self.tempdir, "historical")
        )
        f = override_settings(AIRA_DATA_FORECAST=os.path.join(self.tempdir, "forecast"))
        r = override_settings(AIRA_COEFFS_RASTERS_DIR=self.tempdir)
        d = override_settings(AIRA_DRAINTIME_DIR=self.tempdir)
        c = override_settings(
            CACHES={
                "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
            }
        )
        with h, f, r, d, c:
            calculate_performance_chart(self.agrifield)
            self.results = cache.get("performance_chart_{}".format(self.agrifield.id))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_results(self):
        self.assertAlmostEqual(self.results.applied_water[0], 250.0)
        self.assertAlmostEqual(self.results.applied_water[1], 0.0)
        self.assertAlmostEqual(self.results.applied_water[2], 0.0)
        self.assertAlmostEqual(self.results.applied_water[3], 0.0)
        self.assertEqual(self.results.chart_dates[0], dt.date(2018, 3, 15))
        self.assertEqual(self.results.chart_dates[1], dt.date(2018, 3, 16))
        self.assertEqual(self.results.chart_dates[2], dt.date(2018, 3, 17))
        self.assertEqual(self.results.chart_dates[3], dt.date(2018, 3, 18))
        self.assertAlmostEqual(self.results.chart_ifinal[0], 396.8133333)
        self.assertAlmostEqual(self.results.chart_ifinal[1], 400.0800002)
        self.assertAlmostEqual(self.results.chart_ifinal[2], 400.2666667)
        self.assertAlmostEqual(self.results.chart_ifinal[3], 400.3133335)
        self.assertAlmostEqual(self.results.chart_irr_period_peff_cumulative, 0.96)
        self.assertAlmostEqual(self.results.chart_peff[0], 0.0)
        self.assertAlmostEqual(self.results.chart_peff[1], 0.4)
        self.assertAlmostEqual(self.results.chart_peff[2], 0.32)
        self.assertAlmostEqual(self.results.chart_peff[3], 0.24)
