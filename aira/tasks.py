from __future__ import absolute_import

from datetime import datetime, timedelta
import os
from django.core.cache import cache
from django.conf import settings

from pthelma.swb import SoilWaterBalance

from swb import calculate_soil_water

import pandas as pd

from aira.celery import app
from aira.irma.main import (agripoint_in_raster, common_period_dates,
                            load_meteodata_file_paths, raster2point,
                            rasters2point)
from aira.irma.main import DRAINTIME_A_RASTER, DRAINTIME_B_RASTER
from aira.models import IrrigationLog


class Results():
    pass


def extractSWBTimeseries(agrifield, HRFiles, HEFiles, FRFiles, FEFiles):
    """
        Given a Agrifield extract Timeseries from raster files and
        convert to pd.DataFrame.
    """
    EFFECTIVE_PRECIP_FACTOR = 0.8
    lat, long, kc = agrifield.latitude, agrifield.longitude, agrifield.get_kc

    _r = rasters2point(lat, long, HRFiles)
    _e = rasters2point(lat, long, HEFiles)
    _rf = rasters2point(lat, long, FRFiles)
    _ef = rasters2point(lat, long, FEFiles)
    start, end  = common_period_dates(_r, _e)
    fstart, fend = common_period_dates(_rf, _ef)

    dateIndexH = pd.date_range(start=start.date(), end=end.date(), freq='D')
    dateIndex = pd.date_range(start=start.date(), end=fend.date(), freq='D')

    data = {
        "effective_precipitation": [
            v[1] * EFFECTIVE_PRECIP_FACTOR
            for v in _r.items() if v[0] >= start and v[0] <= end
        ] + [
            v[1] * EFFECTIVE_PRECIP_FACTOR
            for v in _rf.items() if v[0] >= fstart and v[0] <= fend
                and v[0] not in dateIndexH
        ],
        "actual_net_irrigation": False, # Set as default False
        "crop_evapotranspiration":[
            v[1] * float(kc) for v in _e.items()
            if v[0] >= start and v[0] <= end
        ] + [
            v[1] * float(kc) for v in _ef.items()
            if v[0] >= start and v[0] <= fend
                and v[0] not in dateIndexH
        ],
    }
    df = pd.DataFrame(data, index=dateIndex)

    # Update dates with irrigations events
    logs = agrifield.irrigationlog_set.filter(time__range=(start, end))
    for log in logs:
        try:
            date = log.time.date()
            row = df.loc[date]
            df.at[date, "actual_net_irrigation"] = log.applied_water
        except:
            # Insanity check, date does not exist in our original date
            pass

    return {
        "timeseries": df,
        "start": start,
        "end": end,
        "fstart": fstart,
        "fend": fend,
        "draintime_A": raster2point(lat, long, DRAINTIME_A_RASTER),
        "draintime_B": raster2point(lat, long, DRAINTIME_B_RASTER),
    }


def execute_model(agrifield):
    """
    Run pthelma.SoilWaterBalance model on agrifield
    """

    results = Results()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        return results

    # Retrieve precipitation and evaporation time series at the agrifield
    HRFiles, HEFiles, FRFiles, FEFiles = load_meteodata_file_paths()

    # Extract data from files withe pd.DataFrame and end, start dates
    dTimeseries = extractSWBTimeseries(agrifield, HRFiles, HEFiles,
                                       FRFiles, FEFiles)

    ####  Template messages
    if not agrifield.irrigationlog_set.exists():
        results.irrigation_log_not_exists = True

    # Determine last irrigation, if applicable
    last_irrigation = (agrifield.irrigationlog_set.latest()
                       if agrifield.irrigationlog_set.exists() else None)

    start_date_daily = dTimeseries['start'].date()
    end_date_daily = dTimeseries['end'].date()
    f_start_date_daily = dTimeseries['fstart'].date()
    f_end_date_daily = dTimeseries['fend'].date()
    if last_irrigation and ((last_irrigation.time.date() < start_date_daily) or
                            (last_irrigation.time.date() > end_date_daily)):
        last_irrigation = None
        # Template messages
        results.irrigation_log_outside_time_period = True


    # Agrifield parameters
    area = agrifield.area
    theta_fc = agrifield.get_field_capacity
    zr = (float(agrifield.get_root_depth_min) +
          float(agrifield.get_root_depth_max)) / 2
    kc = float(agrifield.get_kc)
    zr_factor = 1000
    irr_eff = float(agrifield.get_efficiency)
    a = dTimeseries['draintime_A']
    b = dTimeseries['draintime_B']

    theta_init = theta_fc
    
    model_params = dict(
        theta_s=float(agrifield.get_thetaS),
        theta_fc=theta_fc,
        theta_wp=agrifield.get_wilting_point,
        zr=zr,
        zr_factor=zr_factor,
        p=float(agrifield.get_mad),
        draintime=round(a * zr ** b),
        theta_init=theta_init,
        mif=1,
        timeseries= dTimeseries['timeseries']
    )

    dresults = calculate_soil_water(**model_params)
    df = dresults['timeseries']
    raw = dresults['raw']
    df['advice'] = df.apply(lambda x: x.dr > raw , axis=1)
    df['ifinal'] = df.apply(lambda x: x.recommended_net_irrigation / irr_eff, axis=1)
    df['ifinal_m3'] = df.apply(lambda x: (x.ifinal / 1000) * area, axis=1)

    results.last_irr_date = last_irrigation.time.date() if last_irrigation else None
    results.sd = dTimeseries['start'].date()  # Starting date of forecast data
    results.ed = dTimeseries['end'].date()   # Finish date of forecast  data
    results.adv = any(df['advice'].tolist())
    results.sdh = f_start_date_daily
    results.edh = f_end_date_daily
    results.ifinal = df.ix[-1, "ifinal"]
    results.ifinal_m3 = (results.ifinal / 1000) * area
    # Keep naming as its due to template rendering
    results.adv_sorted =  [
        [date.date(), row.ks, row.ifinal, row.ifinal_m3]
        for date, row in df.loc[df['advice'] == True].iterrows()
        if date >= pd.Timestamp(results.sdh)
    ]
    # For advice page
    results.swb_report =  [
        [date.date(), row.effective_precipitation, row.dr, row.theta , row.advice, row.ks,  row.ifinal ]
        for date, row in df.iterrows()
        if date >=  pd.Timestamp(results.sdh)
    ]
    # Save results to cache
    cache.set('model_run_{}'.format(agrifield.id), results, None)
    return results


def calculate_performance_chart(agrifield):
    results = Results()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        return results

    # Retrieve precipitation and evaporation time series at the agrifield
    HRFiles, HEFiles, FRFiles, FEFiles = load_meteodata_file_paths()

    # Extract data from files withe pd.DataFrame and end, start dates
    dTimeseries = extractSWBTimeseries(agrifield, HRFiles, HEFiles,
                                       FRFiles, FEFiles)

    # Agrifield parameters
    area = agrifield.area
    theta_fc = agrifield.get_field_capacity
    zr = (float(agrifield.get_root_depth_min) +
          float(agrifield.get_root_depth_max)) / 2
    kc = float(agrifield.get_kc)
    zr_factor = 1000
    irr_eff = float(agrifield.get_efficiency)

    # 16 mar to 16 mart
    theta_init = theta_fc * zr * zr_factor

    model_params = dict(
        theta_s=float(agrifield.get_thetaS),
        theta_fc=theta_fc,
        theta_wp=agrifield.get_wilting_point,
        zr=zr,
        zr_factor=zr_factor,
        p=float(agrifield.get_mad),
        draintime=1,
        theta_init=theta_init,
        mif=1,
        timeseries= dTimeseries['timeseries']
    )

    dresults = calculate_soil_water(**model_params)
    df = dresults['timeseries']
    df['ifinal'] = df.apply(lambda x: x.recommended_net_irrigation / irr_eff, axis=1)

    results.chart_dates = [date.date() for date, row  in df.iterrows()]
    results.chart_ifinal = [
        row.ifinal
        for date, row in df.iterrows()
    ]
    results.chart_peff = [
        row.effective_precipitation
        for date, row in df.iterrows()
    ]
    results.chart_irr_period_peff_cumulative =  sum(results.chart_peff)

    results.applied_water  = []
    results.applied_water  = [
        row.actual_net_irrigation if row.actual_net_irrigation else 0
        for date, row in df.iterrows()
    ]
    cache.set('performance_chart_{}'.format(agrifield.id), results, None)


@app.task
def calculate_agrifield(agrifield):
    cache_key = 'agrifield_{}_status'.format(agrifield.id)
    cache.set(cache_key, 'being processed', None)
    try:
        execute_model(agrifield)
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
