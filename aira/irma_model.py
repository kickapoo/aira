import os
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


def raster2pointTS(lat, log, files):
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(lat, log)
    return extract_point_timeseries_from_rasters(files, point)


def swb_finish_date(precipitation, evapotranspiration):
    plast = precipitation.bounding_dates()[1]
    elast = evapotranspiration.bounding_dates()[1]
    return min(plast, elast)


def run_swb_model(precipitation, evapotranspiration,
                  fc, wp, rd, kc, p, irrigation_efficiency, rd_factor,
                  start_date, initial_soil_moisture, finish_date):
    swb_model = SoilWaterBalance(fc, wp, rd, kc, p,
                                 precipitation, evapotranspiration,
                                 irrigation_efficiency, rd_factor)
    iwa = swb_model.irrigation_water_amount(start_date, initial_soil_moisture,
                                            finish_date)
    return iwa


def irrigation_amount_view(agrifield_id):
    try:
        f = Agrifield.objects.get(pk=agrifield_id)
        # Meteo Parameters
        precip = raster2pointTS(f.lat, f.lon, PRECIP_FILES)
        evap = raster2pointTS(f.lat, f.lon, EVAP_FILES)
        # fc later will be provided from a raster map
        # wp later will be provided from a raster map
        fc = 0.5
        wp = 1
        # Parameters provided from aira.models
        rd = float(f.ct.ct_rd)
        kc = float(f.ct.ct_coeff)
        irrigation_efficiency = float(f.irrt.eff)
        initial_soil_moisture = fc
        p = 1
        rd_factor = 1
        start_date = f.irrigationlog_set.latest().time.replace(tzinfo=None)
        finish_date = swb_finish_date(precip, evap)
        next_irr = run_swb_model(precip, evap, fc, wp, rd, kc, p,
                                 irrigation_efficiency, rd_factor,
                                 start_date, initial_soil_moisture, finish_date)
    except:
        next_irr = None
    return next_irr
