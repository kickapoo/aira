import datetime as dt
import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings

import numpy as np
import pandas as pd
from freezegun import freeze_time
from model_mommy import mommy
from osgeo import gdal, osr

from aira.models import Agrifield, CropType, IrrigationLog, IrrigationType


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
    @classmethod
    def _setup_test_data(cls):
        cls._setup_field_capacity_raster()
        cls._setup_draintime_rasters()
        cls._setup_theta_s_raster()
        cls._setup_pwp_raster()
        cls._setup_meteo_rasters()
        cls._setup_agrifield()

    @classmethod
    def _setup_field_capacity_raster(cls):
        filename = os.path.join(cls.tempdir, "fc.tif")
        setup_input_file(filename, np.array([[1, 1], [1, 1]]), None)

    @classmethod
    def _setup_draintime_rasters(cls):
        filename = os.path.join(cls.tempdir, "a_1d.tif")
        setup_input_file(filename, np.array([[30, 30], [30, 30]]), None)
        filename = os.path.join(cls.tempdir, "b.tif")
        setup_input_file(filename, np.array([[0.95, 0.95], [0.95, 0.95]]), None)

    @classmethod
    def _setup_theta_s_raster(cls):
        filename = os.path.join(cls.tempdir, "theta_s.tif")
        setup_input_file(filename, np.array([[0.5, 0.5], [0.5, 0.5]]), None)

    @classmethod
    def _setup_pwp_raster(cls):
        filename = os.path.join(cls.tempdir, "pwp.tif")
        setup_input_file(filename, np.array([[0.1, 0.1], [0.1, 0.1]]), None)

    @classmethod
    def _setup_meteo_rasters(cls):
        cls._setup_test_raster("rain", "2018-03-15", [[0.0, 0.1], [0.2, 0.3]])
        cls._setup_test_raster("evaporation", "2018-03-15", [[2.1, 2.2], [2.3, 2.4]])
        cls._setup_test_raster("rain", "2018-03-16", [[0.5, 0.6], [0.7, 0.8]])
        cls._setup_test_raster("evaporation", "2018-03-16", [[9.1, 9.2], [9.3, 9.4]])
        cls._setup_test_raster("rain", "2018-03-17", [[0.4, 0.5], [0.6, 0.7]])
        cls._setup_test_raster("evaporation", "2018-03-17", [[9.5, 9.6], [9.7, 9.8]])
        cls._setup_test_raster("rain", "2018-03-18", [[0.3, 0.2], [0.1, 0.0]])
        cls._setup_test_raster("evaporation", "2018-03-18", [[9.6, 9.7], [9.8, 9.9]])

    @classmethod
    def _setup_test_raster(cls, var, datestr, contents):
        subdir = "forecast" if datestr >= "2018-03-18" else "historical"
        filename = os.path.join(
            cls.tempdir, subdir, "daily_{}-{}.tif".format(var, datestr)
        )
        year, month, day = [int(x) for x in datestr.split("-")]
        timestamp = dt.datetime(year, month, day)
        setup_input_file(filename, np.array(contents), timestamp)

    @classmethod
    def _setup_agrifield(cls):
        cls.crop_type = mommy.make(
            CropType,
            name="Grass",
            root_depth_max=0.7,
            root_depth_min=1.2,
            max_allowed_depletion=0.5,
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
        cls.irrigation_type = mommy.make(
            IrrigationType, name="Surface irrigation", efficiency=0.60
        )
        cls.user = mommy.make(User, username="batman", is_active=True)
        cls.agrifield = mommy.make(
            Agrifield,
            owner=cls.user,
            name="A field",
            crop_type=cls.crop_type,
            irrigation_type=cls.irrigation_type,
            location=Point(22.0, 38.0),
            area=2000,
        )
        cls.irrigation_log = mommy.make(
            IrrigationLog,
            agrifield=cls.agrifield,
            time=dt.datetime(2018, 3, 15, 7, 0, tzinfo=dt.timezone.utc),
            applied_water=500,
        )


@freeze_time("2018-03-18 13:00:01")
class ExecuteModelTestCase(TestCase, SetupTestDataMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tempdir = tempfile.mkdtemp()
        os.mkdir(os.path.join(cls.tempdir, "historical"))
        os.mkdir(os.path.join(cls.tempdir, "forecast"))
        cls._setup_test_data()
        h = override_settings(
            AIRA_DATA_HISTORICAL=os.path.join(cls.tempdir, "historical")
        )
        f = override_settings(AIRA_DATA_FORECAST=os.path.join(cls.tempdir, "forecast"))
        s = override_settings(AIRA_DATA_SOIL=cls.tempdir)
        with h, f, s:
            cls.results = cls.agrifield.execute_model()
        cls.timeseries = cls.results["timeseries"]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)
        super().tearDownClass()

    def test_start_date(self):
        self.assertEqual(self.timeseries.index[0], pd.Timestamp("2018-03-15"))

    def test_historical_end_date(self):
        self.assertEqual(
            self.results["historical_end_date"], pd.Timestamp("2018-03-17")
        )

    def test_forecast_start_date(self):
        self.assertEqual(
            self.results["forecast_start_date"], pd.Timestamp("2018-03-18")
        )

    def test_end_date(self):
        self.assertEqual(self.timeseries.index[-1], pd.Timestamp("2018-03-18"))

    def test_ks(self):
        self.assertAlmostEqual(self.timeseries["ks"]["2018-03-18"], 0.8611415)

    def test_ifinal(self):
        self.assertAlmostEqual(self.timeseries["ifinal"]["2018-03-18"], 410.3407445)

    def test_ifinal_m3(self):
        self.assertAlmostEqual(self.timeseries["ifinal_m3"]["2018-03-18"], 820.6814889)

    def test_effective_precipitation(self):
        var = "effective_precipitation"
        self.assertAlmostEqual(self.timeseries[var]["2018-03-15"], 0.0)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-16"], 0.4)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-17"], 0.32)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-18"], 0.24)

    def test_dr(self):
        self.assertAlmostEqual(self.timeseries["dr"]["2018-03-18"], 492.4088933)

    def test_theta(self):
        self.assertAlmostEqual(self.timeseries["theta"]["2018-03-18"], 0.4816748)

    def test_actual_net_irrigation(self):
        var = "actual_net_irrigation"
        self.assertAlmostEqual(self.timeseries[var]["2018-03-15"], 250)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-16"], 0)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-17"], 0)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-18"], 0)

    def test_ifinal_theoretical(self):
        var = "ifinal_theoretical"
        self.assertAlmostEqual(self.timeseries[var]["2018-03-15"], 397.0583333)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-16"], 401.1416669)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-17"], 401.375)
        self.assertAlmostEqual(self.timeseries[var]["2018-03-18"], 401.4333336)
