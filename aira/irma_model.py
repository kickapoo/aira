from osgeo import ogr, osr
from pthelma.spatial import extract_point_timeseries_from_rasters
from pthelma.swb import SoilWaterBalance


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
