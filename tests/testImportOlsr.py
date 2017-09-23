import unittest
import on_geronimo.data_import.import_olsr as olsr


class OLSRTestcase(unittest.TestCase):

    def test_parser_dump(self):
        f = open("olsr.txt", encoding="ascii")
        lines = f.read().splitlines()
        tables = olsr._txtinfo_parser(lines, ("routes", "hna", "topology", "mid", "links"))
        self.assertEqual(len(tables), 5)
        self.assertGreater(len(tables["routes"]), 0)
        self.assertGreater(len(tables["hna"]), 0)
        self.assertGreater(len(tables["topology"]), 0)
        self.assertGreater(len(tables["mid"]), 0)
        self.assertGreater(len(tables["links"]), 0)
        f.close()


if __name__ == "__main__":
    unittest.main()
