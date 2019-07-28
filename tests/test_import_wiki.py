import unittest

from on_geronimo.data_import import import_wiki

from . import IMPORT_WIKI_SAMPLE_FILE


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

    def test_full_node_details(self):
        html_node = """
            <td><a style='color:white; text-decoration:none; background-color:#000000;
                padding:2px;' href='/index.php/AP1.248' title=' 0.00'>AP1.248</a> </td>
            <td> 17:10:04 11.01.15</td>
            <td>Fährstraße Gehlsdorf</td><td>Omni 5dBi</td>
            <td>TP-Link WR1043ND</td>
            <td>Martin</td>
            <td>olsr.on-i.de</td>
            <td>N54.102187 E12.118521</td></tr><tr>"""
        parser = import_wiki.AccessPointTable()
        parser.feed(self.HTML_TABLE_HEADER + html_node + self.HTML_TABLE_FOOTER)
        rows = parser._rows
        self.assertEqual(len(rows), 1)
        self.assertDictEqual(rows[0], {
            "main_ip": "AP1.248",
            "post_address": "Fährstraße Gehlsdorf",
            "antenna": "Omni 5dBi",
            "device": "TP-Link WR1043ND",
            "owner": "Martin",
            "notes": "olsr.on-i.de",
            "latlon": "N54.102187 E12.118521",
        })

    def test_dump_table(self):
        '''parsing a dumped ONI table'''
        with open(IMPORT_WIKI_SAMPLE_FILE, encoding="UTF-8") as f:
            content = f.read()
        parser = import_wiki.AccessPointTable()
        parser.feed(content)
        rows = parser._rows
        self.assertGreater(len(rows), 0)
        nodes = {}
        for row in rows:
            ap_id = row["main_ip"]
            nodes[ap_id] = row
        self.assertIn("AP1.239", nodes.keys())


if __name__ == "__main__":
    unittest.main()