from django.core.management.base import BaseCommand

import geronimo.data_import.import_olsr


class Command(BaseCommand):

    help = "Importieren der AP-Daten via olsrd-txtinfo"

    def handle(self, *args, **options):
        import_args = {}
        if args:
            import_args["txtinfo_url"] = args[0]
        geronimo.data_import.import_olsr.import_routes_from_olsr(**import_args)
