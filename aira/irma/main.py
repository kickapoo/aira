import math
import os

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from hspatial import extract_point_from_raster
from osgeo import gdal


def get_parameters(afield_obj):
    """
        For url:advice, populate  afield_obj
        information table
    """
    # For url 'advice' templates use
    fc = afield_obj.field_capacity
    wp = afield_obj.wilting_point
    rd = (
        float(afield_obj.get_root_depth_min) + float(afield_obj.get_root_depth_max)
    ) / 2
    # FAO table 22 , page 163
    p = float(afield_obj.get_mad)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.get_efficiency)
    theta_s = afield_obj.theta_s
    rd_factor = 1000  # Static for mm
    IRT = afield_obj.get_irrigation_optimizer
    custom_parameters = afield_obj.use_custom_parameters
    last_irrigate = None
    if afield_obj.irrigationlog_set.exists():
        last_irrigate = afield_obj.irrigationlog_set.latest()
        if last_irrigate.applied_water is None:
            rd_factor = 1000
            if not custom_parameters:
                fc = extract_point_from_raster(
                    afield_obj.location,
                    gdal.Open(os.path.join(settings.AIRA_COEFFS_RASTERS_DIR, "fc.tif")),
                )
                wp = extract_point_from_raster(
                    afield_obj.location,
                    gdal.Open(
                        os.path.join(settings.AIRA_COEFFS_RASTERS_DIR, "pwp.tif")
                    ),
                )
            fc_mm = fc * rd * rd_factor
            wp_mm = wp * rd * rd_factor
            taw_mm = fc_mm - wp_mm
            p = float(afield_obj.get_mad)
            raw_mm = p * taw_mm
            last_irrigate.applied_water = (raw_mm * afield_obj.area) / 1000
            last_irrigate.message = _(
                "Irrigation water is estimated using " "system's default parameters."
            )
    return locals()


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
