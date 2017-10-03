# use the default configuration, but overwrite the location of the database

from settings.on_geronimo_api import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": "db.sqlite3",
    }
}
