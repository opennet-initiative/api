from django.core.management.base import BaseCommand

import geronimo.data_import.import_wiki


class Command(BaseCommand):

    help = "Importieren der AP-Daten aus dem Wiki"

    def handle(self, *args, **options):
        geronimo.data_import.import_wiki.import_accesspoints_from_wiki()