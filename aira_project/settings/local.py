import os
from .base import *

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SECRET_KEY = os.urandom(24)


# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [
#             '/Users/kickapoo/Github/IRMA/aira-irma/',
#              os.path.join(PROJECT_ROOT, '../aira/templates/')
#         ],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# STATICFILES_DIRS = ('/Users/kickapoo/Github/IRMA/aira-dashboard/static/',)

# STATICFILES_DIRS = ('/Users/kickapoo/Github/IRMA/aira-irma/static/',)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, '../../aira-irma/locale'),
    os.path.join(PROJECT_ROOT, '../aira/locale/'),
)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "aira",
        "USER": "kickapoo",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/aira_cache',
    },
}

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'anastasiadis.st00@gmail.com'
# EMAIL_HOST_PASSWORD = 'southparkS2'
# EMAIL_PORT = 587
