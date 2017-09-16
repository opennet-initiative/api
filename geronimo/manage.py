#!/usr/bin/env python3

import os
import sys


def main_func():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geronimo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main_func()
