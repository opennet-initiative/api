import logging
import os

from django.test import TestCase

from on_geronimo.data_import.import_olsr import import_routes_from_olsr_data


TEST_ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
IMPORT_OLSR_SAMPLE_FILE = os.getenv("IMPORT_OLSR_SAMPLE_FILE",
                                    os.path.join(TEST_ASSETS_PATH, "olsr.txt"))
IMPORT_ONDATASERVICE_SAMPLE_FILE = os.getenv("IMPORT_OLSR_SAMPLE_FILE",
                                             os.path.join(TEST_ASSETS_PATH, "ondataservice.db"))
IMPORT_WIKI_SAMPLE_FILE = os.getenv("IMPORT_WIKI_SAMPLE_FILE",
                                    os.path.join(TEST_ASSETS_PATH, "wiki_nodes.html"))


# minimize logging output for all tests by default
logging.getLogger().setLevel(logging.ERROR)


def _read_file_content(filename):
    with open(filename, encoding="UTF-8") as f:
        return f.read()


def empty_tables():
    # empty all tables
    for model in (models.AccessPoint, models.EthernetNetworkInterface,
                  models.NetworkInterfaceAddress, models.WifiNetworkInterfaceAttributes,
                  models.RoutingLink, models.InterfaceRoutingLink, models.AccessPointSite):
        model.objects.all().delete()


class TestBase(TestCase):

    @classmethod
    def tearDownClass(cls):
        empty_tables()
        super().tearDownClass()

    @staticmethod
    def import_from_olsr(clear_before=False):
        if clear_before:
            empty_tables()
        data = _read_file_content(IMPORT_OLSR_SAMPLE_FILE)
        import_routes_from_olsr_data(data)
