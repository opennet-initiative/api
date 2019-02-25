from django.core.management.base import BaseCommand

import on_geronimo.data_import.import_olsr


class Command(BaseCommand):

    help = "Importieren der AP-Daten via olsrd-txtinfo"

    def add_arguments(self, parser):
        parser.add_argument("txtinfo_url", nargs="?", help="URL of OLSR httpinfo service")

    def handle(self, *args, **options):
        import_args = {}
        if options["txtinfo_url"]:
            import_args["txtinfo_url"] = options["txtinfo_url"]
        on_geronimo.data_import.import_olsr.import_routes_from_olsr(**import_args)
