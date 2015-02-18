from datetime import timedelta
# Fetch Data files
from aira.irma.config_data import PRECIP_DAILY as d_rain_fps
from aira.irma.config_data import EVAP_DAILY as d_evap_fps
from aira.irma.config_data import PRECIP_HOURLY as h_rain_fps
from aira.irma.config_data import EVAP_HOURLY as h_evap_fps

from aira.irma.config_data import FC_FILE as fc_raster
from aira.irma.config_data import PWP_FILE as pwp_raster
# from aira.irma.config_data import THETA_S_FILE as thetaS_raster

from aira.irma.utils import *

from pthelma.swb import SoilWaterBalance

# Name shorten
# afield = agrifield
# swb = SoilWaterBalance


def get_parameters(afield_obj):
    # For url 'advice' templates use
    fc = raster2point(afield_obj.latitude, afield_obj.longitude, fc_raster)
    wp = raster2point(afield_obj.latitude, afield_obj.longitude, pwp_raster)
    rd = (float(afield_obj.ct.ct_rd_min) + float(afield_obj.ct.ct_rd_max)) / 2
    kc = float(afield_obj.ct.ct_kc)
    p = float(afield_obj.ct.ct_coeff)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.irrt.irrt_eff)
    theta_s = 0.425
    rd_factor = 1000  # Static for mm
    return dict(fc=fc, wp=wp, rd=rd, kc=kc, p=p,
                peff=peff, irr_eff=irr_eff,
                theta_s=theta_s, rd_factor=rd_factor)


def afield2swb(afield_obj, precip, evap):
    # Precip and evap must be pthelma.Timeseries afield_objects
    fc = raster2point(afield_obj.latitude, afield_obj.longitude, fc_raster)
    wp = raster2point(afield_obj.latitude, afield_obj.longitude, pwp_raster)
    rd = (float(afield_obj.ct.ct_rd_min) + float(afield_obj.ct.ct_rd_max)) / 2
    kc = float(afield_obj.ct.ct_kc)
    p = float(afield_obj.ct.ct_coeff)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.irrt.irrt_eff)
    thetaS = 0.425
    rd_factor = 1000  # Static for mm
    swb_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff,
                               thetaS, precip, evap, rd_factor)
    return swb_obj


def run_water_balance(swb_obj, start_date, end_date,
                      theta_init, irr_event_days, Dr_historical):
    return swb_obj, swb_obj.water_balance(theta_init, irr_event_days,
                                          start_date, end_date, Dr_historical)


def run_daily(swb_obj, start_date, theta_init, irr_event_days=[]):
    # start_date: latests.irrigation event
    #             or start_date + 20day for default run
    end_date = data_start_end_date(swb_obj.precip, swb_obj.evap)[1]
    start_date = make_tz_datetime(start_date, flag="D")
    end_date = make_tz_datetime(end_date, flag="D")
    daily_swb, depl_daily = run_water_balance(swb_obj, start_date, end_date,
                                              theta_init, irr_event_days,
                                              Dr_historical=None)
    return daily_swb, depl_daily


def run_hourly(swb_obj, Dr_historical):
    start_date, end_date = data_start_end_date(swb_obj.precip, swb_obj.evap)
    theta_init = 0  # Set to zero as Dr_Historical will replace theta_init
    start_date = make_tz_datetime(start_date, flag="H")
    end_date = make_tz_datetime(end_date, flag="H")
    irr_event_days = []
    hourly_swb, depl_hourly = run_water_balance(swb_obj, start_date, end_date,
                                                theta_init, irr_event_days,
                                                Dr_historical=Dr_historical)
    # Also returns start_date, end_date for use in url 'home'
    return hourly_swb, depl_hourly, start_date, end_date


def advice_date(swb_report):
    irr_dates = [i['date'] for i in swb_report if i['irrigate'] >= 1]
    irr_amount = [i['Ifinal'] for i in swb_report if i['irrigate'] >= 1]
    return dict(zip(irr_dates, irr_amount))


def view_run(afield_obj, flag_run,
             daily_r_fps=d_rain_fps, daily_e_fps=d_evap_fps,
             hourly_r_fps=h_rain_fps, hourly_e_fps=h_evap_fps):
    # Notes:  flag : "irr_event" , "no_irr_event"
    # Load Historical (daily)
    # pthelma.extract_point_from_raster dont have Timeseries.time_step
    precip_daily, evap_daily = load_ts_from_rasters(afield_obj, daily_r_fps,
                                                    daily_e_fps)
    precip_daily.time_step.length_minutes = 1440
    evap_daily.time_step.length_minutes = 1440

    # Load Hourly (Current day + forecast days0
    precip_hourly, evap_hourly = load_ts_from_rasters(afield_obj, hourly_r_fps,
                                                      hourly_e_fps)
    precip_hourly.time_step.length_minutes = 60
    evap_hourly.time_step.length_minutes = 60

    # Create a swb obj daily / hourly
    swb_daily_obj = afield2swb(afield_obj, precip_daily, evap_daily)
    swb_hourly_obj = afield2swb(afield_obj, precip_hourly, evap_hourly)

    if flag_run == "no_irr_event":
        # Run daily with defaults
        start_date = data_start_end_date(precip_daily, evap_daily)[0]
        # Adding 20 days to default run to make it little faster run
        start_date = start_date + timedelta(days=20)
        theta_init = swb_daily_obj.fc_mm - 0.75 * swb_daily_obj.raw_mm
        if start_date.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily_obj.fc_mm
        depl_historical = run_daily(swb_daily_obj, start_date,
                                    theta_init, irr_event_days=[])[1]
        # Hourly (current + forecast)
        swb_view, depl_h, sd, ed = run_hourly(swb_hourly_obj, depl_historical)

    if flag_run == "irr_event":
        theta_init = swb_daily_obj.fc_mm
        start_date = afield_obj.irrigationlog_set.latest().time
        # irr_event_days=[] is set to empty as we start from irrigation event,
        # so initial conditions are known.
        # 'irr_event_days' usage is external pthelma.swb use.
        # For example: user starts run model from irrigation day
        #              and wants to check the scenario
        #              "What is the model performance if field is irrigate
        #              in next (timeseries) days ex. start_date + 2 etc
        # Above comment is set as remainder.
        depl_historical = run_daily(swb_daily_obj, start_date,
                                    theta_init, irr_event_days=[])[1]
        swb_view, depl_h, sd, ed = run_hourly(swb_hourly_obj, depl_historical)
    return swb_view, sd, ed, advice_date(swb_view.wbm_report)
