#!/usr/bin/env python3
#
# load settings from the examples directory
# (to be used in a source checkout directory)
#

import os
import sys


def main_func():
    repo_examples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "examples")
    sys.path.insert(0, repo_examples_dir)
    # allow to discover the settings in a source checkout
    settings_path = os.environ.get("ON_GERONIMO_SETTINGS_DIR", "/etc/on-geronimo")
    sys.path.insert(0, settings_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.on_geronimo_local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main_func()
