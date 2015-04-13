from datetime import timedelta
# Fetch Data files
from aira.irma.utils import FC_FILE as fc_raster
from aira.irma.utils import PWP_FILE as pwp_raster
from aira.irma.utils import THETA_S_FILE as thetaS_raster

from aira.irma.utils import *

from pthelma.swb import SoilWaterBalance

# Name shorten
# afield = agrifield
# swb = SoilWaterBalance


def get_parameters(afield_obj):
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
    return locals()


def get_default_db_value(afield_obj):
    kc = afield_obj.crop_type.kc
    irr_eff = afield_obj.irrigation_type.efficiency
    mad = afield_obj.crop_type.max_allow_depletion
    rd_max = afield_obj.crop_type.root_depth_max
    rd_min = afield_obj.crop_type.root_depth_min
    IRT = afield_obj.irrigation_optimizer
    fc = raster2point(afield_obj.latitude, afield_obj.longitude, fc_raster)
    wp = raster2point(afield_obj.latitude, afield_obj.longitude, pwp_raster)
    thetaS = raster2point(afield_obj.latitude, afield_obj.longitude,
                          thetaS_raster)
    return locals()


def afield2swb(afield_obj, precip, evap):
    # Precip and evap must be pthelma.Timeseries afield_objects
    # HERE 1)
    fc = afield_obj.get_field_capacity
    wp = afield_obj.get_wilting_point
    rd = (float(afield_obj.get_root_depth_min) +
          float(afield_obj.get_root_depth_max)) / 2
    kc = float(afield_obj.get_kc)
    p = float(afield_obj.get_mad)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(afield_obj.get_efficiency)
    thetaS = raster2point(afield_obj.latitude, afield_obj.longitude,
                          thetaS_raster)
    rd_factor = 1000  # Static for mm
    swb_obj = SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff,
                               thetaS, precip, evap, rd_factor)
    return swb_obj


def run_water_balance(swb_obj, start_date, end_date,
                      theta_init, irr_event_days, FC_IRT, Dr0):
    return swb_obj, swb_obj.water_balance(theta_init, irr_event_days,
                                          start_date, end_date, FC_IRT,
                                          Dr0)


def run_daily(swb_obj, start_date, theta_init, FC_IRT, Dr0, irr_event_days=[]):
    # start_date: latests.irrigation event
    #             or start_date     + 20day for default run
    end_date = data_start_end_date(swb_obj.precip, swb_obj.evap)[1]
    start_date = make_tz_datetime(start_date, flag="D")
    end_date = make_tz_datetime(end_date, flag="D")
    daily_swb, depl_daily = run_water_balance(swb_obj, start_date, end_date,
                                              theta_init, irr_event_days,
                                              FC_IRT, Dr0)
    return daily_swb, depl_daily


def run_hourly(swb_obj, FC_IRT, Dr0):
    start_date, end_date = data_start_end_date(swb_obj.precip, swb_obj.evap)
    theta_init = 0  # Set to zero as Dr_Historical will replace theta_init
    start_date = make_tz_datetime(start_date, flag="H")
    end_date = make_tz_datetime(end_date, flag="H")
    irr_event_days = []
    hourly_swb, depl_hourly = run_water_balance(swb_obj, start_date, end_date,
                                                theta_init, irr_event_days,
                                                FC_IRT, Dr0)
    # Also returns start_date, end_date for use in url 'home'
    return hourly_swb, depl_hourly, start_date, end_date


def advice_date(swb_report):
    irr_dates = [i['date'] for i in swb_report if i['irrigate'] >= 1]
    irr_amount = [i['Ifinal'] for i in swb_report if i['irrigate'] >= 1]
    irr_Ks = [i['Ks'] for i in swb_report if i['irrigate'] >= 1]
    irr_values = zip(irr_amount, irr_Ks)
    return dict(zip(irr_dates, irr_values))


def over_fc(swb_report, fc_mm):
    temp_over_search = [True for i in swb_report if i['Dr_i'] >= fc_mm]
    if len(temp_over_search) >= 1:
        return True
    return False


def view_run(afield_obj, flag_run, daily_r_fps,
             daily_e_fps, hourly_r_fps, hourly_e_fps):
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
    # Here form validation
    # fc, thetat_s, wilting_point
    # Create a swb obj daily / hourly
    swb_daily_obj = afield2swb(afield_obj, precip_daily, evap_daily)
    swb_hourly_obj = afield2swb(afield_obj, precip_hourly, evap_hourly)

    if flag_run == "no_irr_event":
        # Run daily with defaults
        start_date = data_start_end_date(precip_daily, evap_daily)[0]
        # Adding 20 days to default run to make it little faster run
        start_date = start_date + timedelta(days=20)
        # Theta init
        theta_init = swb_daily_obj.fc_mm - 0.75 * swb_daily_obj.raw_mm
        if start_date.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily_obj.fc_mm
        FC_IRT = afield_obj.get_irrigation_optimizer
        depl_historical = run_daily(swb_daily_obj, start_date,
                                    theta_init, FC_IRT, Dr0=None,
                                    irr_event_days=[])[1]
        swb_view, depl_h, sd, ed = run_hourly(swb_hourly_obj,
                                              FC_IRT, depl_historical)

    if flag_run == "irr_event":
        start_date = afield_obj.irrigationlog_set.latest().time
        if afield_obj.irrigationlog_set.latest().applied_water in [None, '']:
            theta_init = swb_daily_obj.raw_mm + swb_daily_obj.lowlim_theta_mm
            Dr0 = theta_init - swb_daily_obj.fc_mm
        else:
            rd_f = 1000  # Static for mm
            Inet = (afield_obj.irrigationlog_set.latest().applied_water /
                    afield_obj.area) * rd_f * float(afield_obj.get_efficiency)
            theta_init = Inet + \
                (swb_daily_obj.fc_mm - 0.75 * swb_daily_obj.raw_mm)
            Dr0 = swb_daily_obj.fc_mm - theta_init
        # Why irr_event_days = [] ?
        # irr_event_days=[] is set to empty as we start from irrigation event,
        # so initial conditions are known.
        # 'irr_event_days' usage is external pthelma.swb use.
        # For example: user starts run model from irrigation day
        #              and wants to check the scenario
        #              "What is the model performance if field is irrigate
        #              in next (timeseries) days ex. start_date + 2 etc
        # Above comment is set as a remainder.
        FC_IRT = afield_obj.get_irrigation_optimizer
        depl_historical = run_daily(swb_daily_obj, start_date,
                                    theta_init, FC_IRT, Dr0,
                                    irr_event_days=[])[1]
        swb_view, depl_h, sd, ed = run_hourly(swb_hourly_obj,
                                              FC_IRT, depl_historical)
    ovfc = over_fc(swb_view.wbm_report, swb_view.fc_mm)
    return swb_view, sd, ed, advice_date(swb_view.wbm_report), ovfc
