#!/usr/bin/env python3

import os
import sys


def main_func():
    settings_path = os.environ.get("GERONIMO_SETTINGS_DIR", "/etc/on-geronimo")
    sys.path.insert(0, settings_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.on_geronimo")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main_func()
