import html.parser
import urllib.error
import urllib.parse
import urllib.request
import sys

from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

import geronimo.data_import.opennet
import geronimo.oni_model.models


# "lambda" hilft fuer die verzoegerte Namensaufloesung der Parser-Klassen
NODE_WIKI_PAGES = (
    (lambda: AccessPointTable, "https://wiki.opennet-initiative.de/wiki/Opennet_Nodes"),
    (lambda: ServerTable, "https://wiki.opennet-initiative.de/wiki/Server"),
)


# We need to add 'object' explicitely since HTMLParser.HTMLParser seems to be
# an old-style class (not inherited from 'object'). This causes the exception
# 'TypeError: must be type, not classobj' during the 'super' call.
class _MediaWikiNodeTableParser(html.parser.HTMLParser, object):

    def __init__(self):
        super(_MediaWikiNodeTableParser, self).__init__()
        self._rows = []
        self._row_data = None
        self._column_data = None

    def parse_row_columns(self, columns):
        """ parse a list of row items (one per column)

            Return None for invalid inputs and a dictionary in case of success.
        """
        raise NotImplementedError

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row_data = []
        elif tag == "td":
            self._column_data = []
        else:
            pass

    def handle_endtag(self, tag):
        if tag == "td":
            # Irgendwie landet am Ende der latlon-Daten immer ein "\n" (kein Zeilenumbruch -
            # sondern zwei Zeichen).
            column_text = " ".join(self._column_data).strip().strip("\n")
            # durch html-Entity-Entfernung entstehen ungewollte Leerzeichen
            column_text = column_text.replace(" , ", ", ")
            column_text = column_text.replace("( ", "(")
            column_text = column_text.replace(" )", ")")
            self._row_data.append(column_text)
            self._column_data = None
        elif tag == "tr":
            # proper number of columns?
            if len(self._row_data) == len(self.column_names):
                column_dict = {key: value for key, value in zip(self.column_names, self._row_data)}
                parsed_data = self.parse_row_columns(column_dict)
                if parsed_data:
                    self._rows.append(parsed_data)
            self._row_data = None
        else:
            pass

    def handle_data(self, data):
        if self._column_data is not None:
            data = data.strip()
            if data:
                self._column_data.append(data)

    def get_parsed_items(self):
        return list(self._rows)


class AccessPointTable(_MediaWikiNodeTableParser):

    # the node tables in the opennet wiki contain the following data columns
    column_names = ("main_ip", "lastseen", "post_address", "antenna", "device", "owner", "notes",
                    "latlon")

    def parse_row_columns(self, columns):
        # first data column != "frei"?
        if columns["post_address"].lower() == "frei":
            return None
        # are all data columns (excluding the first two columns) empty?
        if not any([bool(columns[key].strip()) for key in self.column_names[2:]]):
            return None
        # this is a valid column
        result = dict(columns)
        result.pop("lastseen")
        return result


class ServerTable(_MediaWikiNodeTableParser):

    # the server tables in the opennet wiki contain the following data columns
    column_names = ("hostname", "main_ip", "other_ip_v4", "other_ipv6", "post_address", "notes")

    def parse_row_columns(self, columns):
        # ignore servers without a routing IP
        if columns["main_ip"] in (None, "", "-"):
            return
        return {"post_address": "{hostname}, {post_address}".format(**columns),
                "main_ip": columns["main_ip"],
                "notes": columns["notes"]}


def _parse_nodes():
    result = []
    for parser_func, url in NODE_WIKI_PAGES:
        html = urllib.request.urlopen(url).read().decode("utf-8")
        parser = parser_func()()
        parser.feed(html)
        result.extend(parser.get_parsed_items())
    return result


def get_node_by_main_ip_candidates(candidates):
    """ Find a matching AccessPoint with using one of the given IP addresses as its main IP """
    # transform names into IPs (string, not ipaddress)
    candidate_ips = [str(geronimo.data_import.opennet.parse_node_ip(candidate))
                     for candidate in candidates]
    # go through the candiates and look for a matching node
    for ip in candidate_ips:
        try:
            return (ip, geronimo.oni_model.models.AccessPoint.objects.get(main_ip=ip))
        except ObjectDoesNotExist:
            pass
    # No match found? Create a new node by using the first candidate.
    main_ip = candidate_ips[0]
    print("Failed to find an existing AccessPoint with this main IP: {0}".format(main_ip))
    node, created = geronimo.oni_model.models.AccessPoint.objects.get_or_create(main_ip=main_ip)
    return (main_ip, node)


@transaction.atomic
def import_accesspoints_from_wiki():
    # helper function for retrieving column data
    for node_values in _parse_nodes():
        # maybe more than one IP is given (e.g. for servers)
        main_ip_candidates = node_values["main_ip"].split()
        main_ip, node = get_node_by_main_ip_candidates(main_ip_candidates)
        node.post_address = node_values.get("post_address")
        node.antenna = node_values.get("antenna")
        node.device_model = node_values.get("device")
        node.owner = node_values.get("owner")
        node.notes = node_values.get("notes")
        # TODO: enable again?
#       node.pretty_name = geronimo.data_import.opennet.get_pretty_name(node)
        # parse the position
        latlon = node_values.get("latlon")
        if not latlon:
            # we can safely ignore some nodes without position
            if ("test" in node.post_address.lower()) or ("test" in node.notes.lower()):
                pass
            elif node.post_address == "Webserver":
                pass
            else:
                print("Ignoring empty position of node %s: %s" % (main_ip, latlon))
        else:
            lat_replace = lambda text: text.replace("N", "+").replace("S", "-")
            lon_replace = lambda text: text.replace("E", "+").replace("W", "-")
            try:
                lat, lon = latlon.strip().split()
                lon = float(lon_replace(lon))
                lat = float(lat_replace(lat))
            except ValueError:
                # mehr oder weniger als zwei Elemente, bzw. falsches Format
                print("Failed to parse position (%s) of node %s" % (latlon, main_ip),
                      file=sys.stderr)
                lat, lon = None, None
            if lat and lon:
                node.position = Point(lon, lat)
        node.save()


if __name__ == "__main__":
    import_accesspoints_from_wiki()
    nodes = geronimo.oni_model.models.AccessPoint.objects()
    for node in nodes:
        print(repr(node))
    print(len(nodes))
