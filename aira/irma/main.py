import math
import os

from django.conf import settings
from django.core.cache import cache

from hspatial import extract_point_from_raster
from osgeo import gdal


def agripoint_in_raster(obj, mask=None):
    """
        Check if a afield_obj location is
            within 'mask' raster file
    """
    if mask is None:
        mask = os.path.join(settings.AIRA_COEFFS_RASTERS_DIR, "fc.tif")
    try:
        tmp_check = extract_point_from_raster(obj.location, gdal.Open(mask))
    except (RuntimeError, ValueError):
        tmp_check = float("nan")
    return not math.isnan(tmp_check)


def common_period_dates(precip, evap):
    """
        Return common period dates based on
        precipitation and evaporation
        pthlema.timeseries
    """
    pstart = precip.data.index[0]
    estart = evap.data.index[0]
    pend = precip.data.index[-1]
    eend = evap.data.index[-1]

    return max(pstart, estart), min(pend, eend)


class Results:
    pass


def model_results(agrifield):
    return cache.get("model_run_{}".format(agrifield.id))


def get_performance_chart(agrifield):
    return cache.get("performance_chart_{}".format(agrifield.id))
