#!/usr/bin/env python3

import os
import sys


def main_func():
    settings_path = os.environ.get("ON_GERONIMO_SETTINGS_DIR", "/etc/on-geronimo")
    sys.path.insert(0, settings_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.on_geronimo_api")

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        if exc.name == os.environ.get("DJANGO_SETTINGS_MODULE"):
            repo_examples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                             os.path.pardir, "examples")
            sys.path.insert(0, repo_examples_dir)
            execute_from_command_line(sys.argv)
        else:
            raise


if __name__ == "__main__":
    main_func()
