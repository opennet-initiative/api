
import sys
import urllib2
import HTMLParser

import elements
import opennet


URL_NODE_LIST = "http://wiki.opennet-initiative.de/wiki/Opennet_Nodes"
# the node tables in the opennet wiki contain the following data columns
NODE_TABLE_COLUMNS = ("ip_address", "lastseen", "post_address", "antenna", "device", "owner", "notes", "latlon")


# We need to add 'object' explicitely since HTMLParser.HTMLParser seems to be
# an old-style class (not inherited from 'object'). This causes the exception
# 'TypeError: must be type, not classobj' during the 'super' call.
class _MediaWikiNodeTableParser(HTMLParser.HTMLParser, object):

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
            column_text = " ".join(self._column_data)
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
    html = urllib2.urlopen(URL_NODE_LIST).read()
    parser = _MediaWikiNodeTableParser()
    parser.feed(html)
    return parser._rows


def parse_wiki_nodelist(mesh=None, create_new=True):
    rows = _get_node_table_rows()
    if mesh is None:
        mesh = elements.get_mesh()
    # helper function for retrieving column data
    get_column = lambda row, column_name: row[NODE_TABLE_COLUMNS.index(column_name)]
    for row in rows:
        ip_address = opennet.parse_node_ip(get_column(row, "ip_address"))
        if not create_new and not mesh.has_node(ip_address):
            # skip this new node
            continue
        node = mesh.get_node(ip_address)
        # apply attributes
        for key in ("post_address", "antenna", "device", "owner", "notes"):
            value = get_column(row, key)
            if value:
                setattr(node, key, value)
        # parse the position
        latlon = get_column(row, "latlon")
        if latlon:
            splitted = latlon.split()
            lat_replace = lambda text: text.replace("N", "+").replace("S", "-")
            lon_replace = lambda text: text.replace("E", "+").replace("W", "-")
            if len(splitted) == 2:
                for key, text, replace_func in zip(("lat", "lon"), splitted, (lat_replace, lon_replace)):
                    try:
                        value = float(replace_func(text))
                    except ValueError:
                        print >>sys.stderr, "Failed to parse position (%s) of node %s: %s" % (key, ip_address, text)
                        continue
                    setattr(node, key, value)
            else:
                print >>sys.stderr, "Failed to parse position of node %s: %s" % (ip_address, latlon)
    return mesh


if __name__ == "__main__":
    mesh = parse_wiki_nodelist()
    for item in mesh.nodes:
        print repr(item)
    print len(mesh.nodes)

