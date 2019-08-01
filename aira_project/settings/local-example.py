import os

from .base import *

DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SECRET_KEY = os.urandom(24)

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "aira",
        "USER": "aira",
        "PASSWORD": "topsecret",
        "HOST": "localhost",
        "PORT": 5432,
        "CONN_MAX_AGE": 600,
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"": {"handlers": ["console"], "level": "INFO"}},
}
