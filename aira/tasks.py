from __future__ import absolute_import

from datetime import timedelta
import os
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

from pthelma.swb import SoilWaterBalance

from aira.celery import app
from aira.irma.main import (
    agripoint_in_raster, common_period_dates, last_timelog_in_dataperiod,
    load_meteodata_file_paths, raster2point, rasters2point)
from aira.models import IrrigationLog


class Results():
    pass


@app.task
def execute_model(agrifield, Inet_in_forecast):
    """
    Run pthelma.SoilWaterBalance model on agrifield
    """

    results = Results()
    tz_config = timezone.get_default_timezone()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        results.outside_arta_raster = True
        return results

    # Retrieve precipitation and evaporation time series at the agrifield
    daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = \
        load_meteodata_file_paths()
    precip_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                                 daily_r_fps)
    precip_daily.time_step.length_minutes = 1440
    evap_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                               daily_e_fps)
    evap_daily.time_step.length_minutes = 1440
    precip_hourly = rasters2point(agrifield.latitude, agrifield.longitude,
                                  hourly_r_fps)
    precip_hourly.time_step.length_minutes = 60
    evap_hourly = rasters2point(agrifield.latitude, agrifield.longitude,
                                hourly_e_fps)
    evap_hourly.time_step.length_minutes = 60

    # Start and end dates of common dataperiod
    start_date_daily, end_date_daily = common_period_dates(precip_daily,
                                                           evap_daily)
    start_date_hourly, end_date_hourly = common_period_dates(precip_hourly,
                                                             evap_hourly)

    # Agrifield parameters
    fc = agrifield.get_field_capacity
    wp = agrifield.get_wilting_point
    rd = (float(agrifield.get_root_depth_min) +
          float(agrifield.get_root_depth_max)) / 2
    kc = float(agrifield.get_kc)
    p = float(agrifield.get_mad)
    peff = 0.8  # Effective rainfall is 0.8 * Precip
    irr_eff = float(agrifield.get_efficiency)
    thetaS = raster2point(agrifield.latitude, agrifield.longitude,
                          os.path.join(settings.AIRA_COEFFS_RASTERS_DIR,
                                       'theta_s.tif'))
    rd_factor = 1000

    # Create SoilWaterBalance Object for daily and hourly data
    swb_daily = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                 precip_daily, evap_daily, rd_factor)
    swb_hourly = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                  precip_hourly, evap_hourly, rd_factor)

    results.last_irr_event_outside_period = \
        not agrifield.irrigationlog_set.exists()
    results.irr_event = agrifield.irrigationlog_set.exists() and \
        last_timelog_in_dataperiod(agrifield,  precip_daily, evap_daily)
    if results.irr_event:
        results.last_irrigate_date = agrifield.irrigationlog_set.latest().time
    results.flag_run = "no_irr_event" if results.irr_event else "irr_event"

    if (not results.last_irr_event_outside_period) and results.irr_event:
        results.last_irr_date = agrifield.irrigationlog_set.latest().time.\
            replace(hour=0, minute=0)
        # Get theta_init & Dr0 if irrigation event has or not irrigation
        # water amount
        if agrifield.irrigationlog_set.latest().applied_water in [None, '']:
            theta_init = swb_daily.raw_mm + swb_daily.lowlim_theta_mm
            Dr0 = theta_init - swb_daily.fc_mm
        else:
            Inet = (agrifield.irrigationlog_set.latest().applied_water /
                    agrifield.area) * rd_factor * float(
                        agrifield.get_efficiency)
            theta_init = Inet + \
                (swb_daily.fc_mm - 0.75 * swb_daily.raw_mm)
            Dr0 = swb_daily.fc_mm - theta_init

        run_start_date = results.last_irr_date
    else:

        # Start date is historical data finish date minus one day
        # Start data is the previous date
        start_date_daily = end_date_daily - timedelta(days=1)
        # Get theta_init for summer or winter
        theta_init = swb_daily.fc_mm - 0.75 * swb_daily.raw_mm
        if start_date_daily.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily.fc_mm
        run_start_date = start_date_daily
        Dr0 = None

    depl_daily = swb_daily.water_balance(
        theta_init, [], run_start_date.replace(tzinfo=None),
        end_date_daily.replace(tzinfo=None),
        agrifield.get_irrigation_optimizer, Dr0, "NO")
    # Hourly
    swb_hourly.water_balance(0, [], start_date_hourly.replace(tzinfo=None),
                             end_date_hourly.replace(tzinfo=None),
                             agrifield.get_irrigation_optimizer, depl_daily,
                             Inet_in_forecast)

    # Attach to agrifield results from model runs
    # Get the advice and last date ifinal

    # A very special case when the user add irrigation log date outside the
    # period
    last_day_ifinal = [i['Ifinal'] for i in swb_daily.wbm_report
                       if i['date'] == end_date_daily] or [0.0]

    irr_dates = [i['date'] for i in swb_hourly.wbm_report
                 if i['irrigate'] >= 1]
    irr_amount = [i['Ifinal'] for i in swb_hourly.wbm_report
                  if i['irrigate'] >= 1]
    irr_Ks = [i['Ks'] for i in swb_hourly.wbm_report if i['irrigate'] >= 1]
    irr_values = zip(irr_amount, irr_Ks)
    advice = dict(zip(irr_dates, irr_values))

    results.sd = start_date_hourly  # Starting date of forecast data
    results.ed = end_date_hourly  # Finish date of forecast  data
    results.adv = advice  # Advice based on model
    results.sdh = start_date_daily  # Starting date of historical data
    results.edh = end_date_daily  # Finish data of historical data
    results.ifinal = last_day_ifinal[0]  # Model run / last date Water Amount
    results.adv_sorted = sorted(advice.iteritems())  # Sorted advice dates
    results.swb_report = swb_hourly.wbm_report

    cache.set('model_run_{}_{}'.format(agrifield.id, Inet_in_forecast),
              results, None)


@app.task
def calculate_performance_chart(agrifield):
    results = Results()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        results.outside_arta_raster = True
        return results

    daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = \
        load_meteodata_file_paths()
    precip_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                                 daily_r_fps)
    evap_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                               daily_e_fps)
    precip_daily.time_step.length_minutes = 1440
    evap_daily.time_step.length_minutes = 1440
    # precip_daily
    fc = agrifield.get_field_capacity
    wp = agrifield.get_wilting_point
    rd = (float(agrifield.get_root_depth_min) +
          float(agrifield.get_root_depth_max)) / 2
    kc = float(agrifield.get_kc)
    p = float(agrifield.get_mad)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(agrifield.get_efficiency)
    # ThetaS from raster file
    thetaS = raster2point(agrifield.latitude, agrifield.longitude,
                          os.path.join(settings.AIRA_COEFFS_RASTERS_DIR,
                                       'theta_s.tif'))
    rd_factor = 1000  # Unit convertor for mm

    # Create SoilWaterBalance Object for daily and hourly data
    # daily swb
    swb_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                               precip_daily, evap_daily, rd_factor)
    sd, fd = common_period_dates(precip_daily, evap_daily)

    # Irrigation season
    swb_obj.wbm_report = []  # make sure is empty
    irr_period_dates = [i['date'].date() for i in swb_obj.wbm_report]
    irr_period_ifinal = [i['Ifinal'] for i in swb_obj.wbm_report]

    # Concat the data
    chart_dates = irr_period_dates
    chart_ifinal = irr_period_ifinal
    # Get agrifields irrigations log if they exists
    applied_water = [0] * len(chart_dates)
    if agrifield.irrigationlog_set.exists():
        irr_events_objs = IrrigationLog.objects.filter(agrifield=agrifield
                                                       ).all()
        unique_dates = list(set([obj.time.date() for obj in irr_events_objs]))
        for date in unique_dates:
            # 0.0 exist because we can have irrigationlog without any amount
            sum_water = [obj.applied_water or 0.0 for obj
                         in IrrigationLog.objects.filter(
                             agrifield=agrifield, time__contains=date)] or 0.0
            daily_applied_water = sum(sum_water) / agrifield.area * 1000
            if date in chart_dates:
                idx = chart_dates.index(date)
                applied_water[idx] = daily_applied_water
    results.chart_dates = chart_dates
    results.chart_ifinal = chart_ifinal
    results.applied_water = applied_water

    cache.set('performance_chart_{}'.format(agrifield.id), results, None)
