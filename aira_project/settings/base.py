import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@muys-b4q*pe)88^33%xey-%*vgl4wq!fw9z7o99w+ei@l2!_e'

# SECURITY WARNING: don't run with debug turned on in production!
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


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {'default': dj_database_url.config()}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Static Files Path

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

#Setting Registration Backend mail
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#How many days registration mail will be valid
ACCOUNT_ACTIVATION_DAYS = 3
#Where registration.login will Redirect after login
LOGIN_REDIRECT = "/home"
