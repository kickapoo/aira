from __future__ import division
import os
import math
from glob import glob
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


from osgeo import gdal, ogr, osr
from pthelma.spatial import (extract_point_from_raster,
                             extract_point_timeseries_from_rasters)
from pthelma.swb import SoilWaterBalance

from aira.models import IrrigationLog


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
        glob(
            os.path.join(settings.AIRA_DATA_FORECAST, 'hourly_evaporation*.tif'))
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
            fc = raster2point(afield_obj.latitude, afield_obj.longitude, fc_raster)
            wp = raster2point(afield_obj.latitude,
                              afield_obj.longitude, pwp_raster)
            fc_mm = fc * rd * rd_factor
            wp_mm = wp * rd * rd_factor
            taw_mm = fc_mm - wp_mm
            p = float(afield_obj.get_mad)
            raw_mm = p * taw_mm
            last_irrigate.applied_water = (raw_mm * afield_obj.area) / 1000
            last_irrigate.message = _("Irrigation water is estimated using system's default parameters.")
    return locals()


def agripoint_in_raster(obj, mask=FC_FILE):
    """
    	Check if a afield_obj location is
	    within 'mask' raster file
    """
    try:
        tmp_check = raster2point(obj.latitude, obj.longitude, mask)
        if math.isnan(tmp_check):
            return False
        return True
    except:
        return False


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


def last_timelog_in_dataperiod(obj, r_fps, e_fps):
    """
	Search in afield_obj last irrigation event
	is within r_fps, e_fps rasters
    """
    tz_config = timezone.get_default_timezone()
    precip = rasters2point(obj.latitude, obj.longitude,
                                     r_fps)
    evap = rasters2point(obj.latitude, obj.longitude,
                                   e_fps)
    sd, fd = common_period_dates(precip, evap)
    sd = sd.replace(tzinfo=tz_config)
    fd = fd.replace(tzinfo=tz_config)
    # pthlema.timeseries object for Daily data
    # tags datetime with hour=00, minutes=00
    # in order to check in a irrigationlog is in the period,
    # manual addition hour=23 and minute=59 is made
    fd = fd.replace(hour=23, minute=59)
    latest_tl = obj.irrigationlog_set.latest().time
    if latest_tl < sd or latest_tl > fd:
        return False
    return True


class Results():
	pass



def model_run(afield_obj, Inet_in_forecast,
	      daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps):
    """
	Run pthelma.SoilWaterBalance model based on afield_obj
    """
    results = Results()
    tz_config = timezone.get_default_timezone()
    # Check is the afield_obj in study area
    if not agripoint_in_raster(afield_obj):
        results.outside_arta_raster = True
        return results

    # Prepage  Meteological Data as pthelma.timeseries
    precip_daily = rasters2point(afield_obj.latitude, afield_obj.longitude,
                                 daily_r_fps)
    evap_daily = rasters2point(afield_obj.latitude, afield_obj.longitude,
                               daily_e_fps)

    precip_daily.time_step.length_minutes = 1440
    evap_daily.time_step.length_minutes = 1440

    precip_hourly = rasters2point(afield_obj.latitude, afield_obj.longitude,
                                  hourly_r_fps)
    evap_hourly = rasters2point(afield_obj.latitude, afield_obj.longitude,
                                hourly_e_fps)

    precip_hourly.time_step.length_minutes = 60
    evap_hourly.time_step.length_minutes = 60

    # Starting, Finish dates of common dataperiod
    # _d = daily , _h = hourly
    sd_d, fd_d = common_period_dates(precip_daily, evap_daily)
    sd_h, fd_h = common_period_dates(precip_hourly, evap_hourly)
    #  Get afield_obj parameters
    fc = afield_obj.get_field_capacity
    wp = afield_obj.get_wilting_point
    rd = (float(afield_obj.get_root_depth_min) +
          float(afield_obj.get_root_depth_max)) / 2
    kc = float(afield_obj.get_kc)
    p = float(afield_obj.get_mad)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.get_efficiency)
    # ThetaS from raster file
    thetaS = raster2point(afield_obj.latitude, afield_obj.longitude,
                          THETA_S_FILE)
    rd_factor = 1000  # Unit convertor for mm

    # Create SoilWaterBalance Object for daily and hourly data
    # daily swb
    swb_daily_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                     precip_daily, evap_daily, rd_factor)
    # Special message is Inet_in="Yes" in "Since last irrigate..."
    swb_daily_obj_special_message = SoilWaterBalance(fc, wp, rd, kc, p, peff,
                                    irr_eff, thetaS,
                                precip_daily, evap_daily, rd_factor)
    # hourly swb
    swb_hourly_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                      precip_hourly, evap_hourly, rd_factor)

    # Select model run with or without irrigation event
    if afield_obj.irrigationlog_set.exists():
        results.irr_event = True
        results.last_irrigate_date = afield_obj.irrigationlog_set.latest().time
        if last_timelog_in_dataperiod(afield_obj, daily_r_fps, daily_e_fps):
            results.last_irr_event_outside_period = False
            results.flag_run = "irr_event"
            last_irr_date = afield_obj.irrigationlog_set.latest().time
            results.last_irr_date = last_irr_date.replace(tzinfo=tz_config)
            # Get theta_init & Dr0 if irrigation event has or not irrigation
	    # water amount
            if afield_obj.irrigationlog_set.latest().applied_water in [None, '']:
                theta_init = swb_daily_obj.raw_mm + swb_daily_obj.lowlim_theta_mm
                Dr0 = theta_init - swb_daily_obj.fc_mm
            else:
                Inet = (afield_obj.irrigationlog_set.latest().applied_water /
                        afield_obj.area) * rd_factor * float(afield_obj.get_efficiency)
                theta_init = Inet + \
                    (swb_daily_obj.fc_mm - 0.75 * swb_daily_obj.raw_mm)
                Dr0 = swb_daily_obj.fc_mm - theta_init

	        # Daily run, historical depletion , Inet_in = NO
            depl_daily = swb_daily_obj.water_balance(theta_init, [],
                                      last_irr_date.replace(hour=0, minute=0,
                                                            tzinfo=None),
                                      fd_d.replace(tzinfo=None),
                                      afield_obj.get_irrigation_optimizer,Dr0,
                                      "NO")
            swb_daily_obj_special_message.water_balance(theta_init, [],
                                      last_irr_date.replace(hour=0, minute=0,
                                                            tzinfo=None),
                                      fd_d.replace(tzinfo=None),
                                      afield_obj.get_irrigation_optimizer,Dr0,
                                      "NO")

            # Hourly
            swb_hourly_obj.water_balance(0, [], sd_h.replace(tzinfo=None),
                                         fd_h.replace(tzinfo=None),
                                         afield_obj.get_irrigation_optimizer,
                                         depl_daily, Inet_in_forecast)
    else:
        results.irr_event = False
        results.flag_run = "no_irr_event"

        # Start date is historical data finish date minus one day
        # Start data is the previous date
        sd_d = fd_d - timedelta(days=1)
        # Get theta_init for summer or winter
        theta_init = swb_daily_obj.fc_mm - 0.75 * swb_daily_obj.raw_mm
        if sd_d.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily_obj.fc_mm
	# Daily run, historical depletion , Inet_in = NO
        depl_daily = swb_daily_obj.water_balance(theta_init, [],
                                           sd_d.replace(tzinfo=None), fd_d.replace(tzinfo=None),
                                           afield_obj.get_irrigation_optimizer,
                                           None, "NO")
        swb_daily_obj_special_message.water_balance(theta_init, [],
                                  sd_d.replace(tzinfo=None),
                                  fd_d.replace(tzinfo=None),
                                  afield_obj.get_irrigation_optimizer, None,
                                  "NO")
        # Hourly
        swb_hourly_obj.water_balance(0, [], sd_h.replace(tzinfo=None), fd_h.replace(tzinfo=None),
                                     afield_obj.get_irrigation_optimizer,
                                     depl_daily, Inet_in_forecast)

    # Attach to afield_obj results from model runs
    # Get the advice and last date ifinal
    last_day_ifinal = [i['Ifinal'] for i in swb_daily_obj_special_message.wbm_report
                       if i['date'] == fd_d.replace(hour=0, minute=0)]

    irr_dates = [i['date'] for i in swb_hourly_obj.wbm_report if i['irrigate'] >= 1]
    irr_amount = [i['Ifinal'] for i in swb_hourly_obj.wbm_report if i['irrigate'] >= 1]
    irr_Ks = [i['Ks'] for i in swb_hourly_obj.wbm_report if i['irrigate'] >= 1]
    irr_values = zip(irr_amount, irr_Ks)
    advice = dict(zip(irr_dates, irr_values))
    # Make attachment to afield_obj
    results.sd = sd_h # Starting date of forecast  data (_h = _hourly)
    results.ed = fd_h # Finish date of forecast  data (_h = hourly)
    results.adv = advice # Advice based on model
    results.sdh = sd_d # Starting date of historical data (_d = daily)
    results.edh = fd_d # Finish data of historical data (_d = daily)
    results.ifinal = last_day_ifinal[0] # Model run / last date Water Amount
    results.adv_sorted = sorted(advice.iteritems()) # Sorted advice dates
    results.swb_report = swb_hourly_obj.wbm_report

    return results


def email_users_response_data(afield_obj):
   """
     SoilWaterBalance model runs for email_notifications mamagement command
   """
   daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = load_meteodata_file_paths()
   Inet_in_forecast = "YES"

   return model_run(afield_obj, Inet_in_forecast, daily_r_fps, daily_e_fps,
		   hourly_r_fps, hourly_e_fps)

def performance_chart(afield_obj, daily_r_fps, daily_e_fps):
    results = Results()
    precip_daily = rasters2point(afield_obj.latitude, afield_obj.longitude,
                                 daily_r_fps)
    evap_daily = rasters2point(afield_obj.latitude, afield_obj.longitude,
                               daily_e_fps)
    precip_daily.time_step.length_minutes = 1440
    evap_daily.time_step.length_minutes = 1440
    # precip_daily
    fc = afield_obj.get_field_capacity
    wp = afield_obj.get_wilting_point
    rd = (float(afield_obj.get_root_depth_min) +
          float(afield_obj.get_root_depth_max)) / 2
    kc = float(afield_obj.get_kc)
    p = float(afield_obj.get_mad)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.get_efficiency)
    # ThetaS from raster file
    thetaS = raster2point(afield_obj.latitude, afield_obj.longitude,
                          THETA_S_FILE)
    rd_factor = 1000  # Unit convertor for mm

    # Create SoilWaterBalance Object for daily and hourly data
    # daily swb
    swb_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                     precip_daily, evap_daily, rd_factor)
    # Default Greek irrigation period
    sd, fd = common_period_dates(precip_daily, evap_daily)
    non_irr_period_start_date = sd
    non_irr_period_finish_date = datetime(2015, 3, 31)
    irr_period_start_date = datetime(2015, 4, 1)
    irr_period_finish_date = fd

    # Non irrigation season
    dr_non_irr_period = swb_obj.water_balance(swb_obj.fc_mm, [], sd,
                          non_irr_period_finish_date,
                          afield_obj.get_irrigation_optimizer,
                          None, "NO")

    non_irr_period_dates = [i['date'].date() for i in swb_obj.wbm_report]
    non_irr_period_ifinal = [i['Ifinal'] for i in swb_obj.wbm_report]

    # Irrigation season
    swb_obj.wbm_report = [] #  make sure is empty
    # theta_init is zero because Dr_Historical exists
    dr_irr_period = swb_obj.water_balance(0, [], irr_period_start_date, fd,
                              afield_obj.get_irrigation_optimizer,
                              dr_non_irr_period, "YES")
    irr_period_dates = [i['date'].date() for i in swb_obj.wbm_report]
    irr_period_ifinal = [i['Ifinal'] for i in swb_obj.wbm_report]

    # Concat the data
    chart_dates = irr_period_dates
    chart_ifinal = irr_period_ifinal
	# Get agrifields irrigations log if they exists
    applied_water = [0] * len(chart_dates)
    if afield_obj.irrigationlog_set.exists():
        irr_events_objs = IrrigationLog.objects.filter(agrifield=afield_obj).all()
        unique_dates = list(set([obj.time.date() for obj in irr_events_objs]))
        for date in unique_dates:
            # 0.0 exist because we can have irrigationlog without any amount
            sum_water = [obj.applied_water or 0.0  for obj
                        in IrrigationLog.objects.filter(agrifield=afield_obj,
                        time__contains=date)] or 0.0
            daily_applied_water = sum(sum_water) / afield_obj.area * 1000 # m3 --> mm
            if date in chart_dates:
                idx = chart_dates.index(date)
                applied_water[idx] = daily_applied_water
    results.chart_dates = chart_dates
    results.chart_ifinal = chart_ifinal
    results.applied_water = applied_water
    return results
