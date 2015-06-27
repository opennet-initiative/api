from django.core.management.base import BaseCommand, CommandError
import data_import.import_olsr


class Command(BaseCommand):

    help = "Importieren der AP-Daten via olsrd-txtinfo"

    def handle(self, *args, **options):
        data_import.import_olsr.import_routes_from_olsr()

