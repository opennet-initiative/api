# geronimo settings

# load the default settings
from geronimo.settings import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "REALLY_REPLACE_THIS_KEY"


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": "/var/lib/on-geronimo/db.sqlite3",
    }
}


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False