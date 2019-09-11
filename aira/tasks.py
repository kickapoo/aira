import datetime as dt
import os

from django.conf import settings
from django.core.cache import cache

import pandas as pd
from hspatial import PointTimeseries, extract_point_from_raster
from osgeo import gdal
from swb import calculate_crop_evapotranspiration, calculate_soil_water

from aira.celery import app
from aira.irma.main import agripoint_in_raster, common_period_dates


class Results:
    pass


def _point_timeseries(agrifield, category, varname, start_of_season):
    return PointTimeseries(
        agrifield.location,
        prefix=os.path.join(
            getattr(settings, "AIRA_DATA_" + category), "daily_" + varname
        ),
        start_date=start_of_season,
    ).get()


def extractSWBTimeseries(agrifield):
    """
        Given a Agrifield extract Timeseries from raster files and
        convert to pd.DataFrame.
    """
    EFFECTIVE_PRECIP_FACTOR = 0.8

    current_year = dt.date.today().year
    start_of_season = dt.datetime(current_year, 3, 15, 0, 0)

    _r = _point_timeseries(agrifield, "HISTORICAL", "rain", start_of_season)
    _e = _point_timeseries(agrifield, "HISTORICAL", "evaporation", start_of_season)
    _rf = _point_timeseries(agrifield, "FORECAST", "rain", start_of_season)
    _ef = _point_timeseries(agrifield, "FORECAST", "evaporation", start_of_season)

    start, end = common_period_dates(_r, _e)
    fstart, fend = common_period_dates(_rf, _ef)

    dateIndexH = pd.date_range(start=start.date(), end=end.date(), freq="D")
    dateIndex = pd.date_range(start=start.date(), end=fend.date(), freq="D")

    _rfdatapart = _rf.data.loc[fstart:fend]
    _efdatapart = _ef.data.loc[fstart:fend]
    data = {
        "effective_precipitation": (
            (_r.data.loc[start:end, "value"] * EFFECTIVE_PRECIP_FACTOR).tolist()
            + (
                _rfdatapart[~_rfdatapart.index.isin(dateIndexH)]["value"]
                * EFFECTIVE_PRECIP_FACTOR
            ).tolist()
        ),
        "actual_net_irrigation": 0,  # Zero is the default
        "ref_evapotranspiration": (
            (_e.data.loc[start:end, "value"] * EFFECTIVE_PRECIP_FACTOR).tolist()
            + (
                _efdatapart[~_efdatapart.index.isin(dateIndexH)]["value"]
                * EFFECTIVE_PRECIP_FACTOR
            ).tolist()
        ),
    }
    df = pd.DataFrame(data, index=dateIndex)
    calculate_crop_evapotranspiration(
        timeseries=df,
        planting_date=agrifield.crop_type.most_recent_planting_date,
        kc_unplanted=agrifield.crop_type.kc_init,
        kc_ini=agrifield.crop_type.kc_init,
        kc_mid=agrifield.crop_type.kc_mid,
        kc_end=agrifield.crop_type.kc_end,
        init=agrifield.crop_type.days_kc_init,
        dev=agrifield.crop_type.days_kc_dev,
        mid=agrifield.crop_type.days_kc_mid,
        late=agrifield.crop_type.days_kc_late,
    )

    # Update dates with irrigations events
    logs = agrifield.irrigationlog_set.filter(time__range=(start, end))
    for log in logs:
        try:
            date = log.time.date()
            if log.applied_water is None:
                # When an irrigation event has been logged but we don't know how
                # much, we assume we reached field capacity. At that point we use
                # "True" instead of a number, which signals to
                # swb.calculate_soil_water() to assume we irrigated with the recommended
                # amount.
                df.at[date, "actual_net_irrigation"] = True
            else:
                applied_water = float(log.applied_water / agrifield.area * 1000)
                df.at[date, "actual_net_irrigation"] = applied_water
        except Exception:
            # Insanity check, date does not exist in our original date
            pass

    return {
        "timeseries": df,
        "start": start,
        "end": end,
        "fstart": fstart,
        "fend": fend,
        "draintime_A": extract_point_from_raster(
            agrifield.location,
            gdal.Open(os.path.join(settings.AIRA_DRAINTIME_DIR, "a_1d.tif")),
        ),
        "draintime_B": extract_point_from_raster(
            agrifield.location,
            gdal.Open(os.path.join(settings.AIRA_DRAINTIME_DIR, "b.tif")),
        ),
    }


def execute_model(agrifield):
    """
    Run SoilWaterBalance model on agrifield
    """

    results = Results()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        return results

    # Calculate crop evapotranspiration at the agrifield
    dTimeseries = extractSWBTimeseries(agrifield)

    # Set some variables for the template. results.irrigation_log_not_exists is True if
    # there's no irrigation event. Otherwise, results.irrigation_log_outside_time_period
    # is True if, well, what the variaable name says. All this probably shouldn't be
    # here, but in views.
    if not agrifield.irrigationlog_set.exists():
        results.irrigation_log_not_exists = True
    last_irrigation = (
        agrifield.irrigationlog_set.latest()
        if agrifield.irrigationlog_set.exists()
        else None
    )
    start_date_daily = dTimeseries["start"].date()
    end_date_daily = dTimeseries["end"].date()
    if last_irrigation and (
        (last_irrigation.time.date() < start_date_daily)
        or (last_irrigation.time.date() > end_date_daily)
    ):
        last_irrigation = None
        results.irrigation_log_outside_time_period = True
    results.last_irr_date = last_irrigation.time.date() if last_irrigation else None

    # Run swb model and calculate some simple additional columns
    zr = (float(agrifield.root_depth_min) + float(agrifield.root_depth_max)) / 2
    zr_factor = 1000
    irr_eff = float(agrifield.irrigation_efficiency)
    a = dTimeseries["draintime_A"]
    b = dTimeseries["draintime_B"]
    dresults = calculate_soil_water(
        theta_s=float(agrifield.theta_s),
        theta_fc=agrifield.field_capacity,
        theta_wp=agrifield.wilting_point,
        zr=zr,
        zr_factor=zr_factor,
        p=float(agrifield.p),
        draintime=round(a * zr ** b),
        theta_init=agrifield.field_capacity,
        mif=agrifield.irrigation_optimizer,
        timeseries=dTimeseries["timeseries"],
    )
    df = dresults["timeseries"]
    df["advice"] = df.apply(lambda x: x.dr > dresults["raw"], axis=1)
    df["ifinal"] = df.apply(lambda x: x.recommended_net_irrigation / irr_eff, axis=1)
    df["ifinal_m3"] = df.apply(lambda x: (x.ifinal / 1000) * agrifield.area, axis=1)

    # Set some variables in the "results"; these will be used by the template.
    results.sd = dTimeseries["start"].date()
    results.ed = dTimeseries["end"].date()
    results.sdh = dTimeseries["fstart"].date()
    results.edh = dTimeseries["fend"].date()
    results.adv = any(
        [row.advice for date, row in df.iterrows() if date >= pd.Timestamp(results.sdh)]
    )
    results.ifinal = df.ix[-1, "ifinal"]
    results.ifinal_m3 = (results.ifinal / 1000) * agrifield.area
    results.adv_sorted = [
        [date.date(), row.ks, row.ifinal, row.ifinal_m3]
        for date, row in df.loc[df["advice"]].iterrows()
        if date >= pd.Timestamp(results.sdh)
    ]
    results.swb_report = [
        [
            date.date(),
            row.effective_precipitation,
            row.dr,
            row.theta,
            row.advice,
            row.ks,
            row.ifinal,
        ]
        for date, row in df.iterrows()
        if date >= pd.Timestamp(results.sdh)
    ]

    # Save results and return them
    cache.set("model_run_{}".format(agrifield.id), results, None)
    return results


def calculate_performance_chart(agrifield):
    results = Results()

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        return results

    # Extract data from files withe pd.DataFrame and end, start dates
    dTimeseries = extractSWBTimeseries(agrifield)

    # Agrifield parameters
    theta_fc = agrifield.field_capacity
    zr = (float(agrifield.root_depth_min) + float(agrifield.root_depth_max)) / 2
    zr_factor = 1000
    irr_eff = float(agrifield.irrigation_efficiency)
    a = dTimeseries["draintime_A"]
    b = dTimeseries["draintime_B"]

    theta_init = theta_fc

    # We want the model to run ignoring the actual net irrigation, and instead assume
    # that the actual irrigation equals recommended irrigation.
    saved_actual_net_irrigation = dTimeseries["timeseries"]["actual_net_irrigation"]
    dTimeseries["timeseries"]["actual_net_irrigation"] = True

    model_params = dict(
        theta_s=float(agrifield.theta_s),
        theta_fc=theta_fc,
        theta_wp=agrifield.wilting_point,
        zr=zr,
        zr_factor=zr_factor,
        p=float(agrifield.p),
        draintime=round(a * zr ** b),
        theta_init=theta_init,
        mif=agrifield.irrigation_optimizer,
        timeseries=dTimeseries["timeseries"],
    )

    dresults = calculate_soil_water(**model_params)
    df = dresults["timeseries"]
    df["ifinal"] = df.apply(lambda x: x.recommended_net_irrigation / irr_eff, axis=1)

    # We restore the actual net irrigation, which we had ignored for the moment,
    # so that the chart can show it.
    df["actual_net_irrigation"] = saved_actual_net_irrigation

    results.chart_dates = [date.date() for date, row in df.iterrows()]
    results.chart_ifinal = [row.ifinal for date, row in df.iterrows()]
    results.chart_peff = [row.effective_precipitation for date, row in df.iterrows()]
    results.chart_irr_period_peff_cumulative = sum(results.chart_peff)

    results.applied_water = []
    results.applied_water = [
        row.actual_net_irrigation if row.actual_net_irrigation else 0
        for date, row in df.iterrows()
    ]
    cache.set("performance_chart_{}".format(agrifield.id), results, None)


@app.task
def calculate_agrifield(agrifield):
    cache_key = "agrifield_{}_status".format(agrifield.id)
    cache.set(cache_key, "being processed", None)
    try:
        execute_model(agrifield)
        calculate_performance_chart(agrifield)
    except Exception:
        # Oops! We failed. We should probably do something smart here, such as
        # sending the traceback to someone, and possibly requeue the job for
        # a retry, but for now let's just raise the exception, leaving the
        # status at 'being processed'. If the error persists, the field will
        # never be calculated and the user will eventually ask the admins
        # what the heck is going on.
        raise
    cache.set(cache_key, "done", None)
