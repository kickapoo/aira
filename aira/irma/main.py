# Fetch Data files
from aira.irma.config_data import PRECIP_FILES_HISTO as hrain_fps
from aira.irma.config_data import EVAP_FILES_HISTO as hevap_fps
from aira.irma.config_data import PRECIP_FILES_FORE as forain_fps
from aira.irma.config_data import EVAP_FILES_FORE as foevap_fps

from aira.irma.config_data import FC_FILE as fc_raster
from aira.irma.config_data import PWP_FILE as pwp_raster

# Help functions
from aira.irma.utils import *


from pthelma.swb import SoilWaterBalance


def get_parameters(obj):
    # For advice.html
    fc = raster2point(obj.latitude, obj.longitude, fc_raster)
    wp = raster2point(obj.latitude, obj.longitude, pwp_raster)
    rd = (float(obj.ct.ct_rd_min) + float(obj.ct.ct_rd_max)) / 2
    kc = float(obj.ct.ct_kc)
    p = float(obj.ct.ct_coeff)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(obj.irrt.irrt_eff)
    theta_s = 0.42  # LATER TO CHANGE TO THETA_S_RASTER
    rd_factor = 1000  # Static for mm
    return dict(fc=fc, wp=wp, rd=rd, kc=kc, p=p,
                peff=peff, irr_eff=irr_eff,
                theta_s=theta_s, rd_factor=rd_factor)


def make_me_swb(obj, precip, evap):
    # Precip and evap must be pthelma.Timeseries objects
    fc = raster2point(obj.latitude, obj.longitude, fc_raster)
    wp = raster2point(obj.latitude, obj.longitude, pwp_raster)
    rd = (float(obj.ct.ct_rd_min) + float(obj.ct.ct_rd_max)) / 2
    kc = float(obj.ct.ct_kc)
    p = float(obj.ct.ct_coeff)
    peff = 0.8  # Effective rainfall coeff 0.8 * Precip
    irr_eff = float(obj.irrt.irrt_eff)
    theta_s = 0.42  # LATER TO CHANGE TO THETA_S_RASTER
    rd_factor = 1000  # Static for mm
    return SoilWaterBalance(fc, wp, rd, kc, p, peff, irr_eff,
                            theta_s, precip, evap, rd_factor)


def run_water_balance(obj, precip, evap, start_date, end_date,
                      theta_init, irr_event_days, Dr_historical=None):
    swb_agrifield = make_me_swb(obj, precip, evap)
    return swb_agrifield.water_balance(theta_init, irr_event_days, start_date,
                                       end_date, Dr_historical)


def run_forecast(obj, Dr_historical,
                 r_fps=forain_fps, e_fps=foevap_fps):
    precip = load_datasets(obj, r_fps, e_fps)[0]
    precip.time_step.length_minutes = 1440
    evap = load_datasets(obj, r_fps, e_fps)[1]
    evap.time_step.length_minutes = 1440
    start_date, end_date = data_start_end_date(precip, evap)
    theta_init = 0
    start_date = make_tz_datetime(start_date, flag="H")
    end_date = make_tz_datetime(end_date, flag="H")
    irr_event_days = []
    # forecast = run_water_balance(obj, precip, evap, start_date, end_date,
    #                              theta_init, irr_event_days,
    #                              Dr_historical=Dr_historical)
    return "forecast"


def run_historical(obj, theta_init, irr_event_days=[],
                   r_fps=hrain_fps, e_fps=hevap_fps):
    precip = load_datasets(obj, r_fps, e_fps)[0]
    precip.time_step.length_minutes = 60
    evap = load_datasets(obj, r_fps, e_fps)[1]
    evap.time_step.length_minutes = 60
    start_date, end_date = data_start_end_date(precip, evap)
    start_date = make_tz_datetime(start_date, flag="D")
    end_date = make_tz_datetime(end_date, flag="D")
    # historical = run_water_balance(obj, precip, evap, start_date, end_date,
    #                                theta_init, irr_event_days,
    #                                Dr_historical=None)
    return "historical"


def view_run(obj):
    pass
