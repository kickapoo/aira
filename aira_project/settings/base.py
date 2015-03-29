import os
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(BASE_DIR, os.pardir)
PROJECT_ROOT = os.path.abspath(PROJECT_PATH)

SECRET_KEY = os.urandom(24)
DEBUG = False
TEMPLATE_DEBUG = DEBUG
SITE_ID = 1


ALLOWED_HOSTS = []

# DJANGO APPS
DJANGO_APPS = ('django.contrib.admin',
               'django.contrib.auth',
               'django.contrib.contenttypes',
               'django.contrib.sessions',
               'django.contrib.messages',
               'django.contrib.staticfiles',
               'django.contrib.sites',
               'django.contrib.flatpages')

# THIRD_PARTY_APPS
THIRD_PARTY_APPS = ('bootstrap3',
                    'registration',
                    'mathfilters',)
# LOCAL APPS
LOCAL_APPS = ('aira',)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'aira_project.urls'
WSGI_APPLICATION = 'aira_project.wsgi.application'

DATABASES = {}

TIME_ZONE = 'Europe/Athens'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', _('English')),
    ('el', _('Greek')),
)
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)


STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, '../aira/templates/'),
)

ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT = "/home"

AIRA_PARAMETERS_FILE_DIR = os.path.join(PROJECT_ROOT, 'airadb_coeffs')

AIRA_DATA_HISTORICAL = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    "../../../rasters_historical"))

AIRA_DATA_FORECAST = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  "../../../rasters_forecast"))

AIRA_COEFFS_RASTERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "../../../coeffs_data"))
