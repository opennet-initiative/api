"""
WSGI config for on-geronimo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.on_geronimo")

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
