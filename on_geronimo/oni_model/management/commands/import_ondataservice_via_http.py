from django.core.management.base import BaseCommand

from on_geronimo.data_import.import_ondataservice_via_http import (
    import_from_ondataservice_via_http)


class Command(BaseCommand):

    help = "Herunterladen von AP-Daten (im ondataservice-Format) von den Acesspoints"

    def handle(self, *args, **options):
        import_from_ondataservice_via_http(20, dry_run=False,
                                           stdout=self.stdout, stderr=self.stderr)
