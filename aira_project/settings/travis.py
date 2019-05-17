from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'aira',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}
