from django.utils.translation import ugettext_lazy as _

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
                      theta_init, irr_event_days, FC_IRT, Dr0, Inet_in):
    return swb_obj, swb_obj.water_balance(theta_init, irr_event_days,
                                          start_date, end_date, FC_IRT,
                                          Dr0, Inet_in)


def run_daily(swb_obj, start_date, theta_init, FC_IRT, Inet_in,
              Dr0, irr_event_days=[]):
    # start_date: latests.irrigation event
    #             or start_date     + 20day for default run
    end_date = data_start_end_date(swb_obj.precip, swb_obj.evap)[1]
    start_date = make_tz_datetime(start_date, flag="D")
    end_date = make_tz_datetime(end_date, flag="D")
    daily_swb, depl_daily = run_water_balance(swb_obj, start_date, end_date,
                                              theta_init, irr_event_days,
                                              FC_IRT, Dr0, Inet_in)

    last_day_ifinal = [i['Ifinal'] for i in daily_swb.wbm_report if i['date'] == end_date]
    return daily_swb, depl_daily, start_date, end_date, last_day_ifinal[0]


def run_hourly(swb_obj, FC_IRT, Inet_in, Dr0):
    start_date, end_date = data_start_end_date(swb_obj.precip, swb_obj.evap)
    theta_init = 0  # Set to zero as Dr_Historical will replace theta_init
    start_date = make_tz_datetime(start_date, flag="H")
    end_date = make_tz_datetime(end_date, flag="H")
    irr_event_days = []
    hourly_swb, depl_hourly = run_water_balance(swb_obj, start_date, end_date,
                                                theta_init, irr_event_days,
                                                FC_IRT, Dr0, Inet_in)
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


def availiable_data_period(lat=39.15, long=20.98):
    daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = load_meteodata_file_paths()
    arta_rainfall = rasters2point(lat, long, daily_r_fps)
    arta_evap = rasters2point(lat, long, daily_e_fps)
    return data_start_end_date(arta_rainfall, arta_evap)


def view_run(afield_obj, flag_run, Inet_in, daily_r_fps,
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
        # Start date is historical data end date minus one day
        # Start data is the previous date
        start_date = data_start_end_date(precip_daily, evap_daily)[1]
        start_date = start_date - timedelta(days=1)
        # Theta init
        theta_init = swb_daily_obj.fc_mm - 0.75 * swb_daily_obj.raw_mm
        if start_date.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily_obj.fc_mm
        FC_IRT = afield_obj.get_irrigation_optimizer
        Inet_in_h = "NO"
        depl_historical = run_daily(swb_daily_obj, start_date,
                                    theta_init, FC_IRT, Inet_in_h, Dr0=None,
                                    irr_event_days=[])[1]
        swb_view, depl_h, sd, ed = run_hourly(swb_hourly_obj,
                                              FC_IRT, Inet_in, depl_historical)

        # In the flag_run ="irr_event" the start, end historical data is returned
        # so for shortness reasons are set equal to None
        # This comment is a remainder for the future global code review
        start_date, end_date, ifinal  = (None, None, None)

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
        Inet_in_h = "NO"
        daily_swb, depl_daily, start_date, end_date, ifinal = run_daily(swb_daily_obj, start_date,
                                                                theta_init, FC_IRT, Inet_in_h, Dr0,
                                                                irr_event_days=[])
        depl_historical = depl_daily
        swb_view, depl_h, sd, ed = run_hourly(swb_hourly_obj,
                                              FC_IRT, Inet_in, depl_historical)
    ovfc = over_fc(swb_view.wbm_report, swb_view.fc_mm)
    return swb_view, sd, ed, advice_date(swb_view.wbm_report), ovfc, start_date, end_date, ifinal


def email_users_response_data(f):
    daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = load_meteodata_file_paths()
    Inet_in = "YES"
    if not agripoint_in_raster(f):
        f.outside_arta_raster = True
    else:
        if timelog_exists(f):
            f.irr_event = True
            if last_timelog_in_dataperiod(f, daily_r_fps, daily_e_fps):
                f.last_irr_event_outside_period = False
                flag_run = "irr_event"
                swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                    f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                    hourly_r_fps, hourly_e_fps)
                f.adv_sorted = sorted(f.adv.iteritems())
                f.last_irrigate_date = f.irrigationlog_set.latest().time
            else:
                f.last_irr_event_outside_period = True
                flag_run = "no_irr_event"
                swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                    f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                    hourly_r_fps, hourly_e_fps)
                f.adv_sorted = sorted(f.adv.iteritems())
                f.over_fc = ovfc
        else:
            f.irr_event = False
            flag_run = "no_irr_event"
            swb_view, f.sd, f.ed, f.adv, ovfc, f.sdh, f.edh, f.ifinal = view_run(
                f, flag_run, Inet_in, daily_r_fps, daily_e_fps,
                hourly_r_fps, hourly_e_fps)
            f.adv_sorted = sorted(f.adv.iteritems())
            f.over_fc = ovfc
        f.fc_mm = swb_view.fc_mm
    return f
