import os
import glob
from osgeo import ogr, osr
from pthelma.spatial import extract_point_timeseries_from_rasters
from pthelma.swb import SoilWaterBalance


# Meteorological Raster files only for django
raster_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "../../meteo_data"))
precip_files = glob.glob(raster_file_path + '/daily_rain*.tif')
evap_files = glob.glob(raster_file_path + '/daily_evaporation*.tif')


def raster2pointTS(lat, log, files):
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(lat, log)
    return extract_point_timeseries_from_rasters(files, point)


def run_swb_model(lat, log, fc=0.5, wp=1, rd=0.5, kc=0.75, p=1,
                  irrigation_efficiency=1.2, rd_factor=1):

    precipitation = raster2pointTS(lat, log, precip_files)
    evapotranspiration = raster2pointTS(lat, log, precip_files)
    #No logic to check dates ...
    dates = precipitation.bounding_dates()
    start_date = dates[0]
    finish_date = dates[1]
    swb_model = SoilWaterBalance(fc, wp, rd, kc, p,
                                 precipitation, evapotranspiration,
                                 irrigation_efficiency,
                                 rd_factor=1)

    iwa = swb_model.irrigation_water_amount(start_date,
                                            irrigation_efficiency,
                                            finish_date
                                            )
    return iwa
