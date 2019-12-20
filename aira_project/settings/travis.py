from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .base import *  # NOQA

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "aira",
        "USER": "postgres",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

headless = ChromeOptions()
headless.add_argument("--headless")

SELENIUM_WEBDRIVERS = {
    "headless": {
        "callable": webdriver.Chrome,
        "args": [],
        "kwargs": {"options": headless},
    },
}
