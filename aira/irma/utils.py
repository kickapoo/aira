from datetime import datetime
from django.utils import timezone

from aira.irma.config_data import FC_FILE as test_raster
from aira.irma.config_data import PRECIP_FILES_HISTO as hrain_fps
from aira.irma.config_data import EVAP_FILES_HISTO as hevap_fps

from osgeo import gdal, ogr, osr
from pthelma.spatial import (extract_point_from_raster,
                             extract_point_timeseries_from_rasters)


def make_tz_datetime(date, flag="D"):
    # Convert datetime.date object to datetime
    # Also make sure datetime object has
    # settings.base.USE_TZ  default as tzinfo
    tz_config = timezone.get_default_timezone()
    if flag == "D":
        return datetime(date.year,
                        date.month, date.day).replace(tzinfo=tz_config)
    if flag == "H":
        return datetime(date.year, date.month, date.day, date.hour,
                        date.minute).replace(tzinfo=tz_config)


def data_start_end_date(precip, evap):
    # precip & evap must be pthelma.Timeseries objects
    pstart = precip.bounding_dates()[0]
    estart = evap.bounding_dates()[0]
    pend = precip.bounding_dates()[1]
    eend = evap.bounding_dates()[1]
    return max(pstart, estart), min(pend, eend)


def rasters2point(lat, long, files):
    # Convert dataset rasters into
    # pthelma timeseries object
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    return extract_point_timeseries_from_rasters(files, point)


def raster2point(lat, long, file):
    # Convert dataset raster into
    # pthelma timeseries object
    point = ogr.Geometry(ogr.wkbPoint)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    point.AssignSpatialReference(sr)
    point.AddPoint(long, lat)
    f = gdal.Open(file)
    return extract_point_from_raster(point, f)


def load_datasets(obj, r_fps, e_fps):
    precipTS = rasters2point(obj.latitude, obj.longitude, r_fps)
    evapTS = rasters2point(obj.latitude, obj.longitude, e_fps)
    return precipTS, evapTS


def agripoint_in_raster(obj, mask=test_raster):
    # Must be changed to more pythonic way
    try:
        raster2point(obj.latitude, obj.longitude, mask)
        return True
    except:
        return False


def timelog_exists(Agrifield):
    return Agrifield.irrigationlog_set.exists()


def last_timelog_in_dataperiod(obj, r_fps=hrain_fps, e_fps=hevap_fps):
    # Default search against historical data
    precip, evap = load_datasets(obj, r_fps, e_fps)
    sd, fd = data_start_end_date(precip, evap)
    sd = make_tz_datetime(sd, flag="D")
    fd = make_tz_datetime(fd, flag="D")
    latest_tl = obj.irrigationlog_set.latest().time
    if latest_tl < sd or latest_tl > fd:
        return False
    return True
