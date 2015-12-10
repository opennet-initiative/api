from django.core.management.base import BaseCommand, CommandError
import data_import.import_olsr


class Command(BaseCommand):

    help = "Importieren der AP-Daten via olsrd-txtinfo"

    def handle(self, *args, **options):
        if args:
            olsrd_txtinfo_url = args[0]
        else:
            olsrd_txtinfo_url = None
        data_import.import_olsr.import_routes_from_olsr(txtinfo_url=olsrd_txtinfo_url)
