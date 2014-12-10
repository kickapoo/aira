import os
from unipath import Path
import dj_database_url

BASE_DIR = Path(__file__).ancestor(2)
SECRET_KEY = os.urandom(24)
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

# DJANGO APPS
DJANGO_APPS = ('django.contrib.admin',
               'django.contrib.auth',
               'django.contrib.contenttypes',
               'django.contrib.sessions',
               'django.contrib.messages',
               'django.contrib.staticfiles',)

# THIRD_PARTY_APPS
THIRD_PARTY_APPS = ('bootstrap3',
                    'registration',)
# LOCAL APPS
LOCAL_APPS = ('aira',)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'aira_project.urls'
WSGI_APPLICATION = 'aira_project.wsgi.application'

DATABASES = {'default': dj_database_url.config()}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Athens'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = '/static/'
STATICFILES_DIRS = (BASE_DIR.child("static"),)
TEMPLATE_DIRS = (BASE_DIR.child("templates"),)

ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT = "/home"

AIRA_DATA_FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     "../../../meteo_data"))
