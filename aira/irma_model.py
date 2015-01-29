import os
import glob
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from osgeo import gdal, ogr, osr
from pthelma.spatial import (extract_point_from_raster,
                             extract_point_timeseries_from_rasters)
from pthelma.swb import SoilWaterBalance

from aira.models import Agrifield

# GEO_DATA_CONFIG
PRECIP_FILES = glob.glob(os.path.join(settings.AIRA_DATA_FILE_DIR,
                                      'daily_rain*.tif'))
EVAP_FILES = glob.glob(os.path.join(settings.AIRA_DATA_FILE_DIR,
                                    'daily_evaporation*.tif'))
FC_FILE = os.path.join(settings.AIRA_COEFFS_FILE_DIR,
                       'fc.tif')
PWP_FILE = os.path.join(settings.AIRA_COEFFS_FILE_DIR,
                        'pwp.tif')


def rasters2point(lat, long, files):
    # Convert into a pthelma.timeseries
    # a collections of rasters given a point
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    return extract_point_timeseries_from_rasters(files, point)


def raster2point(lat, long, file):
    # Extract single point information
    # from given raster
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    f = gdal.Open(file)
    return extract_point_from_raster(point, f)


def make_tz_datetime(date):
    # Convert datetime.date object to datetime
    # Also make sure datetime object has
    # settings.base.USE_TZ  default as tzinfo
    tz_config = timezone.get_default_timezone()
    return datetime(date.year, date.month, date.day).replace(tzinfo=tz_config)


def swb_finish_date(precipitation, evapotranspiration):
    # Searching for AIRA_DATA_FILE_DIR to find
    # the common time period with the latest record
    # in precipitation and evaporation rasters
    # uses  pthelma.timeseries.bounding_dates method
    plast = precipitation.bounding_dates()[1]
    elast = evapotranspiration.bounding_dates()[1]
    return min(plast, elast)


def data_start_date(precipitation, evapotranspiration):
    # Searching for AIRA_DATA_FILE_DIR to find
    # the common time start date for data availiabiliy
    plast = precipitation.bounding_dates()[0]
    elast = evapotranspiration.bounding_dates()[0]
    return max(plast, elast)


def date_period_warning(agrifield_id):
    warning = None
    f = Agrifield.objects.get(pk=agrifield_id)
    precip = rasters2point(f.latitude, f.longitude, PRECIP_FILES)
    evap = rasters2point(f.latitude, f.longitude, EVAP_FILES)
    data_sd = make_tz_datetime(data_start_date(precip, evap))
    if not f.irrigationlog_set.exists():
        warning = True
        return data_sd, warning
    irr_date = f.irrigationlog_set.latest().time
    irr_date = make_tz_datetime(irr_date)
    if irr_date < data_sd:
        warning = True
        return data_sd, warning
    return data_sd, warning


def irrigation_amount_view(agrifield_id):
    try:
        # Select Agrifield
        f = Agrifield.objects.get(pk=agrifield_id)
        # Create Timeseries given Agrifield location
        precip = rasters2point(f.latitude, f.longitude, PRECIP_FILES)
        evap = rasters2point(f.latitude, f.longitude, EVAP_FILES)
        # Extract pthelma.swb parameter information
        # from aira pre-installed database
        fc = raster2point(f.latitude, f.longitude, FC_FILE)
        wp = raster2point(f.latitude, f.longitude, PWP_FILE)
        rd = float(f.ct.ct_rd)
        kc = float(f.ct.ct_kc)
        irr_eff = float(f.irrt.irrt_eff)
        start_date, warning = date_period_warning(agrifield_id)
        initial_sm = fc
        if warning is True:
            initial_sm = 0
        p = float(f.ct.ct_coeff)
        rd_factor = 1
        finish_date = make_tz_datetime(swb_finish_date(precip, evap))
        # Apply pthelma.swb model
        s = SoilWaterBalance(fc, wp, rd, kc, p,
                             precip, evap,
                             irr_eff, rd_factor)
        # From aira_warings start and finish date
        next_irr = s.irrigation_water_amount(start_date, initial_sm, finish_date)
        next = {'s': s, 'next_irr': str(round(next_irr, 2))}
    except:
        next = {'s': None, 'next_irr': None}
    return next
