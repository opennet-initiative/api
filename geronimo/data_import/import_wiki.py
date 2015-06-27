import sys
import urllib.request, urllib.error, urllib.parse
import html.parser

from django.contrib.gis.geos import Point
from django.db import transaction

import data_import.opennet
import oni_model.models


URL_NODE_LIST = "http://wiki.opennet-initiative.de/wiki/Opennet_Nodes"
# the node tables in the opennet wiki contain the following data columns
NODE_TABLE_COLUMNS = ("ip_address", "lastseen", "post_address", "antenna", "device", "owner", "notes", "latlon")


# We need to add 'object' explicitely since HTMLParser.HTMLParser seems to be
# an old-style class (not inherited from 'object'). This causes the exception
# 'TypeError: must be type, not classobj' during the 'super' call.
class _MediaWikiNodeTableParser(html.parser.HTMLParser, object):

    def __init__(self):
        super(_MediaWikiNodeTableParser, self).__init__()
        self._rows = []
        self._row_data = None
        self._column_data = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row_data = []
        elif tag == "td":
            self._column_data = []
        else:
            pass

    def handle_endtag(self, tag):
        if tag == "td":
            # irgendwie landen am Ende der latlon-Daten immer ein "\n" (kein Zeilenumbruch - sondern zwei Zeichen)
            column_text = " ".join(self._column_data).strip().strip("\n")
            self._row_data.append(column_text)
            self._column_data = None
        elif tag == "tr":
            # proper number of columns?
            # first data column != "frei"?
            # all data columns (excluding the first two columns) empty?
            if (len(self._row_data) == len(NODE_TABLE_COLUMNS)) and \
                    (self._row_data[NODE_TABLE_COLUMNS.index("post_address")].lower() != 'frei') and \
                    "".join(self._row_data[2:]).strip():
                self._rows.append(self._row_data)
            self._row_data = None
        else:
            pass

    def handle_data(self, data):
        if not self._column_data is None:
            data = data.strip()
            if data:
                self._column_data.append(data)


def _get_node_table_rows():
    html = urllib.request.urlopen(URL_NODE_LIST).read().decode("utf-8")
    parser = _MediaWikiNodeTableParser()
    parser.feed(html)
    return parser._rows


@transaction.atomic
def import_accesspoints_from_wiki():
    # helper function for retrieving column data
    get_column = lambda row, column_name: row[NODE_TABLE_COLUMNS.index(column_name)]
    for row in _get_node_table_rows():
        main_ip = data_import.opennet.parse_node_ip(get_column(row, "ip_address"))
        node, created = oni_model.models.AccessPoint.objects.get_or_create(main_ip=main_ip)
        node.post_address = get_column(row, "post_address")
        node.antenna = get_column(row, "antenna")
        node.device_model = get_column(row, "device")
        node.owner = get_column(row, "owner")
        node.notes = get_column(row, "notes")
        #node.pretty_name = data_import.opennet.get_pretty_name(node)
        # parse the position
        latlon = get_column(row, "latlon")
        if not latlon:
            print("Ignoring empty position of node %s: %s" % (main_ip, latlon), file=sys.stderr)
        else:
            lat_replace = lambda text: text.replace("N", "+").replace("S", "-")
            lon_replace = lambda text: text.replace("E", "+").replace("W", "-")
            coordinates = []
            try:
                lat, lon = latlon.strip().split()
                lon = float(lon_replace(lon))
                lat = float(lat_replace(lat))
            except ValueError:
                # mehr oder weniger als zwei Elemente, bzw. falsches Format
                print("Failed to parse position (%s) of node %s" % (latlon, main_ip), file=sys.stderr)
                lat, lon = None, None
            if lat and lon:
                node.position = Point(lon, lat)
        node.save()


if __name__ == "__main__":
    import_accesspoints_from_wiki()
    for item in oni_model.models.AccessPoint.objects():
        print(repr(item))
    print(len(nodes))
