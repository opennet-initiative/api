import urllib.request, urllib.parse, urllib.error
import ipaddress
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


def parse_routes_for_nodes(routes_table):
    for destination, via, metric, etx, interface in routes_table:
        node = mesh.get_node(destination)
        # attach a timestamp
        node.touch()


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
        all_linkers = RoutingLink.objects.filter(interfaceroutinglink__interface=interfaces[0]).filter(interfaceroutinglink__interface=interfaces[1])
        if all_linkers.count() == 1:
            linker = all_linkers[0]
        else:
            if all_linkers.count() > 1:
                all_linkers.delete()
            linker = RoutingLink.objects.create()
            print("Created new RoutingLink %s <-> %s" % (last_hop_ip, destination_ip))
        for interface, qual in zip(interfaces, qualities):
            current_link_info = InterfaceRoutingLink.objects.filter(routing_link=linker, interface=interface)
            if current_link_info.count() > 1:
                # im Zweifel loeschen wir alle LinkRouting-Informationen, da wir aktuelle von alten nicht unterscheiden koennen
                print("Cleaning up superfluous InterfaceRoutingLink objects (%s)" % str(interface.ip_address))
                current_link_info.delete()
            try:
                link_info = InterfaceRoutingLink.objects.filter(routing_link=linker, interface=interface)[0]
                link_info.quality = qual
            except IndexError:
                link_info = InterfaceRoutingLink.objects.create(routing_link=linker, interface=interface, quality=qual)
                print("Created new InterfaceRoutingLink from %s" % interface.ip_address)
            link_info.save()
        linker.save()


def parse_hna_for_ugw(hna_table):
    for destination, gateway in hna_table:
        gateway_node = mesh.get_node(gateway)
        destination = ipaddress.IPNetwork(destination)
        if destination.numhosts == 1:
            gateway_node.ugw = destination[0]


def parse_hna_and_mid_for_alternatives(mid_table, hna_table):
    # HNA-Tabelle vorbereiten: Spalten austauschen; externe HNAs rausfiltern
    for hna, source in hna_table:
        if hna.endswith("/32") and (hna.startswith("192.168.") or hna.startswith("10.")):
            mid_table.append((source, hna[:-3]))
    # the column "alternative" contains one or more IP addresses separated by semicolons
    for main_ip, alternatives in mid_table:
        # Pruefung, ob diese IP-Adresse auch zu einem anderen Objekt gehoert
        found_interface = None
        for interface in EthernetNetworkInterface.objects.filter(ip_address=main_ip):
            if interface.access_point.main_ip != main_ip:
                print("Removing duplicate Network Interface: %s" % str(interface))
                interface.delete()
            else:
                if found_interface:
                    # wir machen erstmal nichts mit diesem Konflikt
                    print("Discovered duplicate APs: %s and %s" % (found_interface, interface))
                found_interface = interface
        if not found_interface:
            ap = AccessPoint.objects.create(main_ip=main_ip)
            print("Created new AP %s" % main_ip)
            ap.save()
            interface = EthernetNetworkInterface.objects.create(ip_address=main_ip, access_point=ap)
            print("Created new NetworkInterface %s" % main_ip)
            interface.save()
        else:
            ap = found_interface.access_point
        for ip_address in alternatives.split(";"):
            interface = EthernetNetworkInterface.objects.filter(access_point=ap, ip_address=ip_address)
            if not interface:
                interface = EthernetNetworkInterface.objects.create(access_point=ap, ip_address=ip_address)
                print("Created new NetworkInterface %s" % ip_address)
                interface.save()

@transaction.atomic
def import_routes_from_olsr(txtinfo_url="http://192.168.10.4:2006"):
    url = "%s/%s" % (txtinfo_url.rstrip("/"), "all")
    topology_lines = urllib.request.urlopen(url).read().decode("ascii").splitlines()
    tables = _txtinfo_parser(topology_lines, ("routes", "hna", "topology", "mid", "links"))
    # first "MID" then "Routes" - otherwise secondary IPs are used for nodes
    parse_hna_and_mid_for_alternatives(tables["mid"], tables["hna"])
    #parse_routes_for_nodes(tables["routes"])
    parse_topology_for_links(tables["topology"], tables["links"])


if __name__ == "__main__":
    import_routes_from_olsr()
    for item in oni_model.models.AccessPoint.objects():
        print(repr(item))
    print(len(nodes))

