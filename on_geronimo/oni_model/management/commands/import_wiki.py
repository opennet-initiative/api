from django.core.management.base import BaseCommand

import on_geronimo.data_import.import_wiki


class Command(BaseCommand):

    help = "Importieren der AP-Daten aus dem Wiki"

    def handle(self, *args, **options):
        on_geronimo.data_import.import_wiki.import_accesspoints_from_wiki()
