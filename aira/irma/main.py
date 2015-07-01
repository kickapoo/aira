from __future__ import division
import os
import math
from glob import glob

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _


from osgeo import gdal, ogr, osr
from pthelma.spatial import (extract_point_from_raster,
                             extract_point_timeseries_from_rasters)


# Raster Static Files with afield_obj parameters values
# FIELD CAPACITY RASTER
FC_FILE = os.path.join(
    settings.AIRA_COEFFS_RASTERS_DIR,
    'fc.tif')

# WILTING POINT RASTER
PWP_FILE = os.path.join(
    settings.AIRA_COEFFS_RASTERS_DIR,
    'pwp.tif')

# THETA_S RASTER
THETA_S_FILE = os.path.join(
    settings.AIRA_COEFFS_RASTERS_DIR,
    'theta_s.tif')


def load_meteodata_file_paths():
    """
        Load meteorological data paths from settings.AIRA_DATA_*
    """
    # Daily
    d_rain_fps = glob(
        os.path.join(settings.AIRA_DATA_HISTORICAL, 'daily_rain*.tif'))
    d_evap_fps = glob(
        os.path.join(settings.AIRA_DATA_HISTORICAL, 'daily_evaporation*.tif'))

    # Contains current day + forecast
    h_rain_fps = glob(os.path.join(settings.AIRA_DATA_HISTORICAL, 'hourly_rain*.tif')) +  \
        glob(os.path.join(settings.AIRA_DATA_FORECAST, 'hourly_rain*.tif'))

    h_evap_fps = glob(os.path.join(settings.AIRA_DATA_HISTORICAL, 'hourly_evaporation*.tif')) +  \
        glob(os.path.join(settings.AIRA_DATA_FORECAST,
                          'hourly_evaporation*.tif'))
    return d_rain_fps, d_evap_fps, h_rain_fps, h_evap_fps


def rasters2point(lat, long, files):
    """
        Convert a series of raster files to single
        point pthelma.timeseries obj
    """
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    return extract_point_timeseries_from_rasters(files, point)


def raster2point(lat, long, file):
    """
        Convert a single raster file to single
        point pthelma.timeseries obj
    """
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    f = gdal.Open(file)
    return extract_point_from_raster(point, f)


def get_default_db_value(afield_obj):
    """
       doc str is missing
    """
    kc = afield_obj.crop_type.kc
    irr_eff = afield_obj.irrigation_type.efficiency
    mad = afield_obj.crop_type.max_allow_depletion
    rd_max = afield_obj.crop_type.root_depth_max
    rd_min = afield_obj.crop_type.root_depth_min
    IRT = afield_obj.irrigation_optimizer
    fc = raster2point(afield_obj.latitude, afield_obj.longitude, FC_FILE)
    wp = raster2point(afield_obj.latitude, afield_obj.longitude, PWP_FILE)
    thetaS = raster2point(afield_obj.latitude, afield_obj.longitude,
                          THETA_S_FILE)
    return locals()


def get_parameters(afield_obj):
    """
        For url:advice, populate  afield_obj
        information table
    """
    # For url 'advice' templates use
    fc = afield_obj.get_field_capacity
    wp = afield_obj.get_wilting_point
    rd = (float(afield_obj.get_root_depth_min) +
          float(afield_obj.get_root_depth_max)) / 2
    kc = float(afield_obj.get_kc)
    # FAO table 22 , page 163
    p = float(afield_obj.get_mad)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.get_efficiency)
    theta_s = afield_obj.get_thetaS
    rd_factor = 1000  # Static for mm
    IRT = afield_obj.get_irrigation_optimizer
    custom_parameters = afield_obj.use_custom_parameters
    last_irrigate = None
    if afield_obj.irrigationlog_set.exists():
        last_irrigate = afield_obj.irrigationlog_set.latest()
        if last_irrigate.applied_water is None:
            rd_factor = 1000
            fc = raster2point(afield_obj.latitude, afield_obj.longitude,
                              FC_FILE)
            wp = raster2point(afield_obj.latitude,
                              afield_obj.longitude, PWP_FILE)
            fc_mm = fc * rd * rd_factor
            wp_mm = wp * rd * rd_factor
            taw_mm = fc_mm - wp_mm
            p = float(afield_obj.get_mad)
            raw_mm = p * taw_mm
            last_irrigate.applied_water = (raw_mm * afield_obj.area) / 1000
            last_irrigate.message = _(
                "Irrigation water is estimated using "
                "system's default parameters.")
    return locals()


def agripoint_in_raster(obj, mask=FC_FILE):
    """
        Check if a afield_obj location is
            within 'mask' raster file
    """
    try:
        tmp_check = raster2point(obj.latitude, obj.longitude, mask)
    except RuntimeError:
        tmp_check = float('nan')
    return not math.isnan(tmp_check)


def common_period_dates(precip, evap):
    """
        Return common period dates based on
        precipitation and evaporation
        pthlema.timeseries
    """
    pstart = precip.bounding_dates()[0]
    estart = evap.bounding_dates()[0]
    pend = precip.bounding_dates()[1]
    eend = evap.bounding_dates()[1]

    return max(pstart, estart), min(pend, eend)


class Results():
        pass


def model_results(agrifield, Inet_in_forecast):
    return cache.get('model_run_{}_{}'.format(agrifield.id, Inet_in_forecast))


def email_users_response_data(agrifield):
    """
    SoilWaterBalance model runs for email_notifications mamagement command
    """
    return model_results(agrifield, "YES")


def get_performance_chart(agrifield):
    return cache.get('performance_chart_{}'.format(agrifield.id))
