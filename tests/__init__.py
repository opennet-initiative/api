import logging
import os

from django.test import TestCase

from on_geronimo.data_import.import_olsr import import_routes_from_olsr_data
from on_geronimo.data_import.import_ondataservice import import_from_ondataservice
from on_geronimo.data_import.import_wiki import import_parsed_wiki_accesspoints, AccessPointTable
import on_geronimo.oni_model.models as models
from on_geronimo.oni_model.sites import SiteUpdater


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

    @staticmethod
    def import_from_ondataservice(clear_before=False):
        if clear_before:
            empty_tables()
        import_from_ondataservice(db_file=IMPORT_ONDATASERVICE_SAMPLE_FILE)

    @staticmethod
    def import_from_wiki(clear_before=False):
        if clear_before:
            empty_tables()
        parser = AccessPointTable()
        data = _read_file_content(IMPORT_WIKI_SAMPLE_FILE)
        parser.feed(data)
        import_parsed_wiki_accesspoints(parser.get_parsed_items())

    @classmethod
    def import_from_all_sources(cls, clear_before=False):
        if clear_before:
            empty_tables()
        cls.import_from_olsr(clear_before=False)
        cls.import_from_wiki(clear_before=False)
        cls.import_from_ondataservice(clear_before=False)
        SiteUpdater().update_sites()
