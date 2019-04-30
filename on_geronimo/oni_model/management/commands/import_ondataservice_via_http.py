from django.core.management.base import BaseCommand

from on_geronimo.data_import.import_ondataservice_via_http import (
    import_from_ondataservice_via_http)


class Command(BaseCommand):

    help = "Herunterladen von AP-Daten (im ondataservice-Format) von den Acesspoints"

    def add_arguments(self, parser):
        parser.add_argument("addresses", nargs="*", type=str)

    def handle(self, *args, addresses=None, **options):
        import_from_ondataservice_via_http(
            stdout=self.stdout, stderr=self.stderr, wanted_addresses=(addresses or None))
