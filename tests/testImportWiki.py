import unittest
from geronimo.data_import import import_wiki


class TestImportWiki(unittest.TestCase):

    HTML_TABLE_HEADER = """
        <table ><tr><th>Nr.</th>
        <th> zuletzt gesehen</th>
        <th>Standort</th>
        <th>Antenne und Richtung</th>
        <th>Typ</th>
        <th>Eigentümer</th>
        <th>Kommentar</th>
        <th>Position</th></tr><tr>"""
    HTML_TABLE_FOOTER = "</table>"

    def setUp(self):  # noqa: N802
        self.parser = import_wiki._MediaWikiNodeTableParser()

    def test_full_node_details(self):
        html_node = """
            <td><a style='color:white; text-decoration:none; background-color:#000000;
                padding:2px;' href='/index.php/AP1.248' title=' 0.00'>AP1.248</a> </td>
            <td> 17:10:04 11.01.15</td>
            <td>Fährstraße Gehlsdorf</td><td>Omni 5dBi</td>
            <td>TP-Link WR1043ND</td>
            <td>Martin Brettschneider</td>
            <td>olsr.on-i.de</td>
            <td>N54.102187 E12.118521</td></tr><tr>"""
        self.parser.feed(self.HTML_TABLE_HEADER + html_node + self.HTML_TABLE_FOOTER)
        rows = self.parser._rows
        self.assertEqual(len(rows), 1)
        self.assertListEqual(rows[0], ["AP1.248", "17:10:04 11.01.15", "Fährstraße Gehlsdorf",
                                       "Omni 5dBi", "TP-Link WR1043ND", "Martin Brettschneider",
                                       "olsr.on-i.de", "N54.102187 E12.118521"])

    def test_dump_table(self):
        '''parsing a dumped ONI table'''
        f = open("wiki_nodes.html", encoding="UTF-8")
        content = f.read()
        f.close()
        self.parser.feed(content)
        rows = self.parser._rows
        self.assertGreater(len(rows), 0)
        nodes = {}
        for row in rows:
            ap_id = row[0]
            nodes[ap_id] = row
        self.assertIn("AP1.239", nodes.keys())


if __name__ == "__main__":
    unittest.main()
