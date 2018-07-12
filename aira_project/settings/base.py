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


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'aira2'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aira_project.urls'
WSGI_APPLICATION = 'aira_project.wsgi.application'

DATABASES = {}
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', _('English')),
    ('el', _('Greek')),
)
# LOCALE_PATHS = (
#     os.path.join(PROJECT_ROOT, '../aira/locale'),
# )
TIME_ZONE = 'Europe/Athens'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 "django.contrib.auth.context_processors.auth",
#                 "django.core.context_processors.debug",
#                 "django.core.context_processors.i18n",
#                 "django.core.context_processors.media",
#                 "django.core.context_processors.static",
#                 "django.core.context_processors.tz",
#                 "django.contrib.messages.context_processors.messages",
#                 "aira.context_processors.map",
#             ]
#         },
#     },
# ]

# ACCOUNT_ACTIVATION_DAYS = 3
# LOGIN_REDIRECT_URL = "/home"
#
# # Celery
# BROKER_URL = 'django://'
#
# AIRA_DATA_HISTORICAL = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                                     "../../../rasters_historical"))
#
# AIRA_DATA_FORECAST = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                                   "../../../rasters_forecast"))
#
# AIRA_COEFFS_RASTERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                               "../../../coeffs_data"))
