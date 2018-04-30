from datetime import datetime, timedelta
from pthelma.swb import SoilWaterBalance

from .utils import (load_meteodata_file_paths, common_period_dates,
                    rasters2point, agripoint_in_raster)


def execute_model(agrifield, Inet_in_forecast):
    """ Execute pthelma.SoilWaterBalance model based on Agrifield parameters.

        Args:
            agrifield: aira.models.Agrifield instance
            Inet_in_forecast (string): 'YES' or 'NO'

        Returns:
            dict: A dictonary with various model
                {
                    "agrifield": (str) Agrifield Name ex. Field 1,
                    "agrigield_id: Agrifield id,
                    "owner": (str) Agrifield Owner
                    "inet": (str),
                    "forecast_sdd": (str) date format: "%Y-%m-%d %H:%M:%S",
                    "forecast_edd": (str) date format: "%Y-%m-%d %H:%M:%S",
                    "historical_sdd": (str) date format: "%Y-%m-%d %H:%M:%S",
                    "historical_edd": (str) date format: "%Y-%m-%d %H:%M:%S"),
                    "has_advice": True or  False,
                    "advice": [
                        {
                        'date': (str) date format: "%Y-%m-%d %H:%M:%S"),
                        'ifinal': (float),
                        'ifinal_m3': (float),
                        'ks': (float),
                        }
                    ]
                    "last_day": {
                        "ifinal": (float),
                        "ifinal_m3": (float)
                    }
        Note:
            Return values (dict) is stored as string to AdviceLog instance with
            Foreign Key to Agrifield.
    """

    # Verify that the agrifield is in study area
    if not agripoint_in_raster(agrifield):
        return {}

    # DATA FILE PATHS
    dr_fps, de_fps, hr_fps, he_fps = load_meteodata_file_paths()
    precip_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                                 dr_fps)
    precip_daily.time_step.length_minutes = 1440
    evap_daily = rasters2point(agrifield.latitude, agrifield.longitude,
                               de_fps)
    evap_daily.time_step.length_minutes = 1440
    precip_hourly = rasters2point(agrifield.latitude, agrifield.longitude,
                                  hr_fps)
    precip_hourly.time_step.length_minutes = 60
    evap_hourly = rasters2point(agrifield.latitude, agrifield.longitude,
                                he_fps)
    evap_hourly.time_step.length_minutes = 60

    # Common Dates Periods daily / hourly
    sdd, edd = common_period_dates(precip_daily, evap_daily)
    sdh, edh = common_period_dates(precip_hourly, evap_hourly)

    # Get Agrifield parameter values
    agroparameters = agrifield.agroparameters()
    rd_factor = 1000
    # SoilWaterBalance Objects for Daily and Hourly data
    swb_daily = SoilWaterBalance(
        agroparameters['fc'], agroparameters['wp'], agroparameters['rd'],
        agroparameters['kc'], agroparameters['mad'], 0.8,
        agroparameters['irr_eff'], agroparameters['thetaS'],
        precip_daily, evap_daily, rd_factor
    )
    swb_hourly = SoilWaterBalance(
        agroparameters['fc'], agroparameters['wp'], agroparameters['rd'],
        agroparameters['kc'], agroparameters['mad'], 0.8,
        agroparameters['irr_eff'], agroparameters['thetaS'],
        precip_hourly, evap_hourly, rd_factor
    )

    # Determine Dr0, theta_init, and run_start_date
    if agrifield.has_irrigation_in_period(sdd.date(), edd.date()):
        applied_water = agrifield.last_irrigation().applied_water
        if not applied_water:
            theta_init = swb_daily.raw_mm + swb_daily.lowlim_theta_mm
            Dr0 = theta_init - swb_daily.fc_mm
        else:
            theta_init = applied_water / agrifield.area * rd_factor * \
                         agroparameters['irr_eff'] + swb_daily.fc_mm - \
                         agroparameters['IRT'] * swb_daily.raw_mm
            Dr0 = swb_daily.fc_mm - theta_init
        run_sd = agrifield.last_irrigation().time.date()
    else:
        run_sd = edd.date() - timedelta(days=1)
        theta_init = swb_daily.fc_mm - agroparameters['IRT'] * swb_daily.raw_mm
        if run_sd.month in [10, 11, 12, 1, 2, 3]:
            theta_init = swb_daily.fc_mm
        Dr0 = None

    # Run the model
    depl_daily = swb_daily.water_balance(
        theta_init, [],
        datetime.combine(run_sd, datetime.min.time()),
        datetime.combine(edd.date(), datetime.min.time()),
        agroparameters['IRT'],
        Dr0, "NO"
    )
    swb_daily.water_balance(
        theta_init, [],
        datetime.combine(run_sd, datetime.min.time()),
        datetime.combine(edd.date(), datetime.min.time()),
        agroparameters['IRT'],
        None, "NO"
    )

    swb_hourly.water_balance(
        0, [],
        sdh.replace(tzinfo=None),
        edh.replace(tzinfo=None),
        agroparameters['IRT'],
        depl_daily, Inet_in_forecast)

    # GET RESULTS
    advice = []
    last_day_ifinal = 0.0
    for model_row in swb_hourly.wbm_report:
        if model_row['irrigate'] >= 1:
            advice.append({
                'date': model_row['date'].strftime("%Y-%m-%d %H:%M:%S"),
                'ifinal': model_row['Ifinal'],
                'ifinal_m3': (model_row['Ifinal'] / 1000) * agrifield.area,
                'ks': model_row['Ks'],
            })
        if model_row['date'] == datetime.combine(edd, datetime.min.time()):
            last_day_ifinal = model_row['Ifinal']

    results = {
        "agrifield": agrifield.name,
        'agrifield_id': agrifield.id,
        "owner": agrifield.owner.username,
        "inet": Inet_in_forecast,
        "forecast_sdd": sdh.strftime("%Y-%m-%d %H:%M:%S"),
        "forecast_edd": edh.strftime("%Y-%m-%d %H:%M:%S"),
        "historical_sdd": sdd.strftime("%Y-%m-%d %H:%M:%S"),
        "historical_edd": edd.strftime("%Y-%m-%d %H:%M:%S"),
        "has_advice": True if advice else False,
        "advice": advice,
        "last_day": {
            "ifinal": last_day_ifinal,
            "ifinal_m3": (last_day_ifinal / 1000) * agrifield.area,
        }
    }
    return results
