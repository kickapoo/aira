import os
from glob import glob
from django.conf import settings

# Daily
PRECIP_DAILY = glob(os.path.join(
    settings.AIRA_DATA_HISTORICAL,
    'daily_rain*.tif'
))

EVAP_DAILY = glob(os.path.join(
    settings.AIRA_DATA_HISTORICAL,
    'daily_evaporation*.tif')
)

# Contains current day + forecast
PRECIP_HOURLY = glob(os.path.join(settings.AIRA_DATA_HISTORICAL, 'hourly_rain*.tif')) +  \
    glob(os.path.join(settings.AIRA_DATA_FORECAST, 'hourly_rain*.tif'))

EVAP_HOURLY = glob(os.path.join(settings.AIRA_DATA_HISTORICAL, 'hourly_evaporation*.tif')) +  \
    glob(os.path.join(settings.AIRA_DATA_FORECAST, 'hourly_evaporation*.tif'))

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
