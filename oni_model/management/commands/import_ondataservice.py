from django.core.management.base import BaseCommand, CommandError
import data_import.import_ondataservice


class Command(BaseCommand):

    args = "db_file"
    help = "Importieren der AP-Daten aus einer lokalen ondataservice-Datenbank"

    def handle(self, *args, **options):
        kwargs = {}
        if args:
            kwargs["db_file"] = args[0]
        data_import.import_ondataservice.import_from_ondataservice(**kwargs)

