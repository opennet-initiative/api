import os


TEST_ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
IMPORT_OLSR_SAMPLE_FILE = os.getenv("IMPORT_OLSR_SAMPLE_FILE",
                                    os.path.join(TEST_ASSETS_PATH, "olsr.txt"))
IMPORT_ONDATASERVICE_SAMPLE_FILE = os.getenv("IMPORT_OLSR_SAMPLE_FILE",
                                             os.path.join(TEST_ASSETS_PATH, "ondataservice.db"))
IMPORT_WIKI_SAMPLE_FILE = os.getenv("IMPORT_WIKI_SAMPLE_FILE",
                                    os.path.join(TEST_ASSETS_PATH, "wiki_nodes.html"))
