import os
import math
from glob import glob
from osgeo import gdal, ogr, osr
from django.conf import settings
from pthelma.spatial import (extract_point_from_raster,
                             extract_point_timeseries_from_rasters)


FC_FILE = os.path.join(settings.AIRA_COEFFS_RASTERS_DIR, 'fc.tif')
PWP_FILE = os.path.join(settings.AIRA_COEFFS_RASTERS_DIR, 'pwp.tif')
THETA_S_FILE = os.path.join(settings.AIRA_COEFFS_RASTERS_DIR, 'theta_s.tif')


def load_meteodata_file_paths():
    """
        Load meteorological data paths from settings.AIRA_DATA_*

        Usage: Checking the avaliable data period
    """
    historical_path = settings.AIRA_DATA_HISTORICAL
    forecast_path = settings.AIRA_DATA_FORECAST
    # Daily
    d_rain_fps = glob(os.path.join(historical_path, 'daily_rain*.tif'))
    d_evap_fps = glob(os.path.join(historical_path, 'daily_evaporation*.tif'))

    # Contains current day + forecast
    h_rain_fps = glob(os.path.join(historical_path, 'hourly_rain*.tif')) +  \
                 glob(os.path.join(forecast_path, 'hourly_rain*.tif'))

    h_evap_fps = glob(os.path.join(historical_path, 'hourly_evaporation*.tif')) +  \
                 glob(os.path.join(forecast_path, 'hourly_evaporation*.tif'))
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


def agrifield_meteo_data(agrifield):
    """ Pthlema daily rainfall and evaporation timeseries from raster files

        Args:
            agrifield: aira.models.Agrifield instance

        Returns:
            tuple: rainfall, evap

        Notes:
            This function is a very ugly way to get data for aira advisor page.
            It will be changed from new Pthlema (panda) included version
    """
    daily_r_fps, daily_e_fps, hps, hps = load_meteodata_file_paths()
    precip_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                                 daily_r_fps)
    evap_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                               daily_e_fps)
    return precip_daily, evap_daily


def agrifield_meteo_forecast_data(agrifield):
    """ Pthlema forecast (hourly) rainfall and evaporation timeseries
        from raster files

        Args:
            agrifield: aira.models.Agrifield instance

        Returns:
            tuple: rainfall, evap

        Notes:
            This function is a very ugly way to get data for aira advisor page.
            It will be changed from new Pthlema (panda) included version
    """
    dfps, dfps, hourly_r_fps, hourly_e_fps = load_meteodata_file_paths()
    precip_hourly = rasters2point(agrifield.latitude, agrifield.longitude,
                                  hourly_r_fps)
    evap_hourly = rasters2point(agrifield.latitude, agrifield.longitude,
                                hourly_e_fps)
    return precip_hourly, evap_hourly


def agripoint_in_raster(obj, mask=FC_FILE):
    """
        Check if a afield_obj location is
            within 'mask' raster file
    """
    try:
        tmp_check = raster2point(obj.latitude, obj.longitude, mask)
    except (RuntimeError, ValueError):
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

# def get_parameters(afield_obj):
#     """
#         For url:advice, populate  afield_obj
#         information table
#     """
#     # For url 'advice' templates use
#     agroparameters = afield_obj.agroparameters()
#
#     fc = agroparameters['fc']
#     wp = agroparameters['wp']
#     rd = agroparameters['rd']
#     kc = agroparameters['kc']
#     # FAO table 22 , page 163
#     p = agroparameters['mad']
#     peff = 0.8  # Effective rainfall coeff 0.8 * Precip
#     irr_eff = agroparameters['irr_eff']
#     theta_s = agroparameters['thetaS']
#     rd_factor = 1000  # Static for mm
#     IRT = agroparameters['IRT']
#     custom_parameters = agroparameters['custom_parms']
#
#     last_irrigate = None
#     if afield_obj.irrigationlog_set.exists():
#         last_irrigate = afield_obj.irrigationlog_set.latest()
#         if last_irrigate.applied_water is None:
#             rd_factor = 1000
#             if not custom_parameters:
#                 fc = raster2point(afield_obj.latitude, afield_obj.longitude,
#                                   FC_FILE)
#                 wp = raster2point(afield_obj.latitude,
#                                   afield_obj.longitude, PWP_FILE)
#             fc_mm = fc * rd * rd_factor
#             wp_mm = wp * rd * rd_factor
#             taw_mm = fc_mm - wp_mm
#             p = agroparameters['mad']
#             raw_mm = p * taw_mm
#             last_irrigate.applied_water = (raw_mm * afield_obj.area) / 1000
#             last_irrigate.message = _(
#                 "Irrigation water is estimated using "
#                 "system's default parameters.")
#     return locals()
