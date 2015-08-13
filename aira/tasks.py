from __future__ import absolute_import

from datetime import datetime, timedelta
import os
from django.core.cache import cache
from django.conf import settings

from pthelma.swb import SoilWaterBalance

from aira.celery import app
from aira.irma.main import (agripoint_in_raster, common_period_dates,
                            load_meteodata_file_paths, raster2point,
                            rasters2point)
from aira.models import IrrigationLog


class Results():
    pass


def execute_model(agrifield, Inet_in_forecast):
    """
    Run pthelma.SoilWaterBalance model on agrifield
    """

    results = Results()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
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

    # Start and end dates of common data period
    start_date_daily, end_date_daily = common_period_dates(precip_daily,
                                                           evap_daily)
    start_date_daily = start_date_daily.date()
    end_date_daily = end_date_daily.date()
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
    thetaS = float(agrifield.get_thetaS)
    IRT = agrifield.get_irrigation_optimizer
    area = agrifield.area
    rd_factor = 1000

    # Create SoilWaterBalance Object for daily and hourly data
    swb_daily = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                 precip_daily, evap_daily, rd_factor)
    swb_last_day_ifinal = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff,
                                 thetaS, precip_daily, evap_daily, rd_factor)
    swb_hourly = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                                  precip_hourly, evap_hourly, rd_factor)

    # Template messages
    if not agrifield.irrigationlog_set.exists():
        results.irrigation_log_not_exists = True

    # Determine last irrigation, if applicable
    last_irrigation = (agrifield.irrigationlog_set.latest()
                       if agrifield.irrigationlog_set.exists() else None)

    if last_irrigation and ((last_irrigation.time.date() < start_date_daily) or
                            (last_irrigation.time.date() > end_date_daily)):
        last_irrigation = None
        # Template messages
        results.irrigation_log_outside_time_period = True

    # Determine Dr0, theta_init, and run_start_date
    if last_irrigation:
        results.last_irr_date = last_irrigation.time.date()
        applied_water = last_irrigation.applied_water
        if applied_water is None:
            theta_init = swb_daily.raw_mm + swb_daily.lowlim_theta_mm
            Dr0 = theta_init - swb_daily.fc_mm
        else:
            theta_init = applied_water / agrifield.area * rd_factor * \
                float(agrifield.get_efficiency) + swb_daily.fc_mm - \
                IRT * swb_daily.raw_mm
            Dr0 = swb_daily.fc_mm - theta_init
        run_start_date = results.last_irr_date
    else:
        start_date_daily = end_date_daily - timedelta(days=1)
        theta_init = swb_daily.fc_mm - IRT * swb_daily.raw_mm
        if start_date_daily.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily.fc_mm
        run_start_date = start_date_daily
        Dr0 = None

    # Run the model
    depl_daily = swb_daily.water_balance(
        theta_init, [], datetime.combine(run_start_date, datetime.min.time()),
        datetime.combine(end_date_daily, datetime.min.time()),
        agrifield.get_irrigation_optimizer, Dr0, "NO")
    swb_last_day_ifinal.water_balance(
        theta_init, [], datetime.combine(run_start_date, datetime.min.time()),
        datetime.combine(end_date_daily, datetime.min.time()),
        agrifield.get_irrigation_optimizer, None, "NO")
    swb_hourly.water_balance(0, [], start_date_hourly.replace(tzinfo=None),
                             end_date_hourly.replace(tzinfo=None),
                             agrifield.get_irrigation_optimizer, depl_daily,
                             Inet_in_forecast)

    # Store results
    last_day_ifinal = [i['Ifinal'] for i in swb_last_day_ifinal.wbm_report
                       if i['date'] == datetime.combine(end_date_daily,
                                            datetime.min.time()) ] or [0.0]
    irr_dates = [i['date'] for i in swb_hourly.wbm_report
                 if i['irrigate'] >= 1]
    irr_amount = [(i['Ifinal'], i['Ifinal']/1000 * area)
                  for i in swb_hourly.wbm_report
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
    results.ifinal_m3 = (results.ifinal/1000) * area
    results.adv_sorted = sorted(advice.iteritems())  # Sorted advice dates
    results.swb_report = swb_hourly.wbm_report

    # Save results to cache
    cache.set('model_run_{}_{}'.format(agrifield.id, Inet_in_forecast),
              results, None)


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
    thetaS = float(agrifield.get_thetaS)
    rd_factor = 1000  # Unit convertor for mm

    # Create SoilWaterBalance Object for daily and hourly data
    # daily swb
    swb_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff, thetaS,
                               precip_daily, evap_daily, rd_factor)
    # Default Greek irrigation period
    sd, fd = common_period_dates(precip_daily, evap_daily)
    non_irr_period_finish_date = datetime(2015, 3, 31)
    irr_period_start_date = datetime(2015, 4, 1)

    # Non irrigation season
    dr_non_irr_period = swb_obj.water_balance(
        swb_obj.fc_mm, [], sd, non_irr_period_finish_date,
        agrifield.get_irrigation_optimizer, None, "NO")

    # Irrigation season
    swb_obj.wbm_report = []  # make sure is empty
    # theta_init is zero because Dr_Historical exists
    swb_obj.water_balance(
        0, [], irr_period_start_date, fd, agrifield.get_irrigation_optimizer,
        dr_non_irr_period, "YES")
    irr_period_dates = [i['date'].date() for i in swb_obj.wbm_report]
    irr_period_ifinal = [i['Ifinal'] for i in swb_obj.wbm_report]
    irr_period_peff = [i['Peff'] for i in swb_obj.wbm_report]
    irr_period_peff_cumulative = sum(irr_period_peff)

    # Concat the data
    chart_dates = irr_period_dates
    chart_ifinal = irr_period_ifinal
    chart_peff = irr_period_peff
    chart_irr_period_peff_cumulative = irr_period_peff_cumulative
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
    results.chart_peff = chart_peff
    results.chart_irr_period_peff_cumulative = chart_irr_period_peff_cumulative
    results.applied_water = applied_water

    cache.set('performance_chart_{}'.format(agrifield.id), results, None)


@app.task
def calculate_agrifield(agrifield):
    cache_key = 'agrifield_{}_status'.format(agrifield.id)
    cache.set(cache_key, 'being processed', None)
    try:
        execute_model(agrifield, 'YES')
        execute_model(agrifield, 'NO')
        calculate_performance_chart(agrifield)
    except:
        # Oops! We failed. We should probably do something smart here, such as
        # sending the traceback to someone, and possibly requeue the job for
        # a retry, but for now let's just raise the exception, leaving the
        # status at 'being processed'. If the error persists, the field will
        # never be calculated and the user will eventually ask the admins
        # what the heck is going on.
        raise
    cache.set(cache_key, 'done', None)
