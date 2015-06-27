import urllib.request, urllib.parse, urllib.error
import datetime
from django.db import transaction
from oni_model.models import AccessPoint, EthernetNetworkInterface, RoutingLink, InterfaceRoutingLink


def _txtinfo_parser(lines, table_names):
    current_table = None
    skip_next = False
    tables = {}
    for line in lines:
        if skip_next:
            skip_next = False
        elif not line:
            current_table = None
        elif current_table in table_names:
            tables[current_table].append(line.split())
        elif current_table:
            pass
        else:
            prefix, next_table = line.split(None, 1)
            assert prefix == "Table:"
            matching_names = [name for name in table_names if name.upper() == next_table.upper()]
            if matching_names:
                current_table = matching_names[0]
                tables[current_table] = []
            else:
                current_table = next_table
            # the next line contains the header
            skip_next = True
    return tables


def _parse_olsr_float(text):
    return float(text.replace("INFINITE", "inf"))


def parse_topology_for_links(mesh, topology_table, neighbour_link_table):
    # remove the 3rd column from the neighbour link table ("Hysteresis")
    combined_table = topology_table + [item[:2] + item[3:] for item in neighbour_link_table]
    for destination, last_hop, lq, nlq, cost in combined_table:
        link = mesh.get_link((destination, last_hop))
        link.cost = _parse_olsr_float(cost)
        link.lq, link.nlq = _parse_olsr_float(lq), _parse_olsr_float(nlq)
    # the node itself can only be discovered here - make sure that its timestamp is current
    if neighbour_link_table:
        local_node = mesh.get_node(neighbour_link_table[0][0])
        local_node.touch()


def parse_topology_for_links(topology_table, neighbour_link_table):
    # remove the 3rd column from the neighbour link table ("Hysteresis")
    combined_table = topology_table + [item[:2] + item[3:] for item in neighbour_link_table]
    for destination_ip, last_hop_ip, lq, nlq, cost in combined_table:
        qualities = (_parse_olsr_float(lq), _parse_olsr_float(nlq))
        interfaces = []
        for ip_address in (last_hop_ip, destination_ip):
            try:
                interface = EthernetNetworkInterface.objects.filter(ip_address=ip_address)[0]
            except IndexError:
                ap, created = AccessPoint.objects.get_or_create(main_ip=ip_address)
                if created:
                    print ("Created new AP %s" % ip_address)
                interface = EthernetNetworkInterface.objects.create(access_point=ap, ip_address=ip_address)
                print("Created new NetworkInterface %s" % ip_address)
                ap.save()
                interface.save()
            interfaces.append(interface)
        linker, created = interfaces[0].get_or_create_link_to(interfaces[1])
        if created:
            print("Created new RoutingLink %s <-> %s" % (last_hop_ip, destination_ip))
        for interface, qual in zip(interfaces, qualities):
            link_info = InterfaceRoutingLink.objects.filter(routing_link=linker, interface=interface)[0]
            link_info.quality = qual
            link_info.save()
        linker.save()
        #update AP timestamps
        for ip_address in (last_hop_ip, destination_ip):
            interface = EthernetNetworkInterface.objects.filter(ip_address=ip_address)[0]
            ap = interface.access_point
            ap.lastseen_timestamp=datetime.datetime.now(datetime.timezone.utc)
            ap.save()


def parse_mid_for_alternatives(mesh, mid_table):
    # the column "alternative" contains one or more IP addresses separated by semicolons
    for main_ip, alternatives in mid_table:
        node = mesh.get_node(main_ip)
        for alternative in alternatives.split(";"):
            node.add_address(alternative)


def parse_olsr_topology(mesh=None, txtinfo_url="http://localhost:2006"):
    url = "%s/%s" % (txtinfo_url.rstrip("/"), "all")
    topology_lines = urllib.request.urlopen(url).read().splitlines()
    tables = _txtinfo_parser(topology_lines, ("routes", "hna", "topology", "mid", "links"))
    if mesh is None:
        mesh = elements.get_mesh()
    # first "MID" then "Routes" - otherwise secondary IPs are used for nodes
    parse_hna_and_mid_for_alternatives(tables["mid"], tables["hna"])
    parse_topology_for_links(tables["topology"], tables["links"])


if __name__ == "__main__":
    mesh = parse_olsr_topology()
    for item in mesh.links:
        print(repr(item))
