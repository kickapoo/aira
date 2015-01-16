import os
from datetime import datetime
import glob
from django.conf import settings

from osgeo import ogr, osr
from pthelma.spatial import extract_point_timeseries_from_rasters
from pthelma.swb import SoilWaterBalance

from aira.models import Agrifield

# GEO_DATA_CONFIG
PRECIP_FILES = glob.glob(os.path.join(settings.AIRA_DATA_FILE_DIR,
                                      'daily_rain*.tif'))
EVAP_FILES = glob.glob(os.path.join(settings.AIRA_DATA_FILE_DIR,
                                    'daily_evaporation*.tif'))


def raster2pointTS(lat, long, files):
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    return extract_point_timeseries_from_rasters(files, point)


def make_datetime(date):
    # Convert datetime.date object to datetime
    return datetime(date.year, date.month, date.day)


def swb_finish_date(precipitation, evapotranspiration):
    plast = precipitation.bounding_dates()[1]
    elast = evapotranspiration.bounding_dates()[1]
    return min(plast, elast)


def irrigation_amount_view(agrifield_id):
    try:
        # Select Agrifield
        f = Agrifield.objects.get(pk=agrifield_id)
        # Create Point Meteo Timeseries
        precip = raster2pointTS(f.latitude, f.longitude, PRECIP_FILES)
        evap = raster2pointTS(f.latitude, f.longitude, EVAP_FILES)
        # fc later will be provided from a raster map
        # wp later will be provided from a raster map
        fc = 0.5
        wp = 1
        # Parameters provided management comand - populate_coeffs
        rd = float(f.ct.ct_rd)
        kc = float(f.ct.ct_coeff)
        irr_eff = float(f.irrt.irrt_eff)
        # Initial Soil moisture is constant
        initial_sm = fc
        p = 1
        rd_factor = 1
        # TZinfo is important for the web, check also settings.base
        start_date = f.irrigationlog_set.latest().time.replace(tzinfo=None)
        start_date = make_datetime(start_date)
        # Depends on the latest AIRA_DATA_FILE
        finish_date = make_datetime(swb_finish_date(precip, evap))
        s = SoilWaterBalance(fc, wp, rd, kc, p,
                             precip, evap,
                             irr_eff, rd_factor)
        next_irr = s.irrigation_water_amount(start_date, initial_sm, finish_date)
        next = {'s': s, 'next_irr': str(round(next_irr, 2))}
    except:
        next = {'s': None, 'next_irr': None}
    return next
