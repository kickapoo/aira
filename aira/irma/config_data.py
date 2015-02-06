import os
import glob

from django.conf import settings

# GEO_DATA_CONFIG_HISTORICAL
PRECIP_FILES_HISTO = glob.glob(os.path.join(
    settings.AIRA_DATA_HISTORICAL,
    'daily_rain*.tif'
))

EVAP_FILES_HISTO = glob.glob(os.path.join(
    settings.AIRA_DATA_HISTORICAL,
    'daily_evaporation*.tif')
)

# os.path.join(settings.AIRA_DATA_HISTORICAL, 'hourly_rain*.tif')[:24]

# GEO_DATA_CONFIG_FORECAST
PRECIP_FILES_FORE = glob.glob(os.path.join(
    settings.AIRA_DATA_FORECAST,
    'hourly_rain*.tif'))

EVAP_FILES_FORE = glob.glob(os.path.join(
    settings.AIRA_DATA_FORECAST,
    'hourly_evaporation*.tif'))

# FIELD CAPACITY RASTER
FC_FILE = os.path.join(
    settings.AIRA_COEFFS_RASTERS_DIR,
    'fc.tif')

# WILTING POINT RASTER
PWP_FILE = os.path.join(
    settings.AIRA_COEFFS_RASTERS_DIR,
    'pwp.tif')
