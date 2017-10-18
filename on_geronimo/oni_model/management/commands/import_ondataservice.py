import argparse

from django.core.management.base import BaseCommand

import on_geronimo.data_import.import_ondataservice


class Command(BaseCommand):

    args = "db_file"
    help = "Importieren der AP-Daten aus einer lokalen ondataservice-Datenbank"

    def add_arguments(self, parser):
        parser.add_argument('database_file', nargs='?', type=argparse.FileType("r"))

    def handle(self, *args, **options):
        kwargs = {}
        if options["database_file"]:
            kwargs["db_file"] = options["database_file"].name
        on_geronimo.data_import.import_ondataservice.import_from_ondataservice(**kwargs)
