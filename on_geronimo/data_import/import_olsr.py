import datetime
import ipaddress
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.db import transaction
from django.utils import timezone

from on_geronimo.oni_model.models import (
    AccessPoint, EthernetNetworkInterface, InterfaceRoutingLink, NetworkInterfaceAddress)


NETMASK_PREFIXLEN = 16


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
            if prefix in {"Version:"}:
                continue
            assert prefix == "Table:", "Expected 'Table:', received '{}' instead".format(prefix)
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


def parse_topology_for_links(topology_table, neighbour_link_table):
    # remove the 3rd column from the neighbour link table ("Hysteresis")
    combined_table = topology_table + [item[:2] + item[3:] for item in neighbour_link_table]
    for destination_ip, last_hop_ip, lq, nlq, cost in combined_table:
        qualities = (_parse_olsr_float(lq), _parse_olsr_float(nlq))
        interfaces = []
        for ip_address in (last_hop_ip, destination_ip):
            interface = EthernetNetworkInterface.objects.filter(
                addresses__address=ip_address).first()
            if interface is None:
                ap, created = AccessPoint.objects.get_or_create(main_ip=ip_address)
                if created:
                    logging.info("Created new AP %s", ip_address)
                interface = EthernetNetworkInterface.objects.create(accesspoint=ap)
                address_object = NetworkInterfaceAddress.create_with_ipaddress(
                    interface,
                    ipaddress.ip_interface("{}/{:d}".format(ip_address, NETMASK_PREFIXLEN)))
                logging.info("Created new NetworkInterface %s", ip_address)
                ap.save()
                interface.save()
                address_object.save()
            interfaces.append(interface)
        linker, created = interfaces[0].get_or_create_link_to(interfaces[1])
        if created:
            logging.info("Created new RoutingLink %s <-> %s", last_hop_ip, destination_ip)
        for interface, qual in zip(interfaces, qualities):
            link_info = InterfaceRoutingLink.objects.filter(routing_link=linker,
                                                            interface=interface)[0]
            link_info.quality = qual
            link_info.save()
        linker.save()
        # update AP timestamps
        for ip_address in (last_hop_ip, destination_ip):
            interface = EthernetNetworkInterface.objects.filter(
                addresses__address=ip_address).first()
            ap = interface.accesspoint
            ap.lastseen_timestamp = timezone.now()
            ap.save()


def parse_hna_and_mid_for_alternatives(mid_table, hna_table):
    # HNA-Tabelle vorbereiten: Spalten austauschen; externe HNAs rausfiltern
    for hna, source in hna_table:
        if hna.endswith("/32") and (hna.startswith("192.168.") or hna.startswith("10.")):
            mid_table.append((source, hna[:-3]))
    # the column "alternative" contains one or more IP addresses separated by semicolons
    for one_mid_entry in mid_table:
        main_ip = one_mid_entry[0]
        alternatives = []
        for alternative in one_mid_entry[1:]:
            alternatives.extend(alternative.split(";"))
        # Pruefung, ob diese IP-Adresse auch zu einem anderen Objekt gehoert
        found_interface = None
        for interface in EthernetNetworkInterface.objects.filter(addresses__address=main_ip):
            if interface.accesspoint.main_ip != main_ip:
                logging.warning("Removing duplicate Network Interface: %s", interface)
                interface.delete()
            else:
                if found_interface:
                    # wir machen erstmal nichts mit diesem Konflikt
                    logging.warning("Removing duplicate APs: %s and %s",
                                    found_interface, interface)
                    # remove both
                    interface.delete()
                    found_interface.delete()
                    found_interface = None
                found_interface = interface
        if not found_interface:
            ap, created = AccessPoint.objects.get_or_create(main_ip=main_ip)
            if created:
                logging.info("Created new AP %s", main_ip)
            interface = EthernetNetworkInterface.objects.create(accesspoint=ap)
            address_object = NetworkInterfaceAddress.create_with_ipaddress(
                interface, ipaddress.ip_interface("{}/{:d}".format(main_ip, NETMASK_PREFIXLEN)))
            logging.info("Created new NetworkInterface %s", main_ip)
            ap.save()
            interface.save()
            address_object.save()
        else:
            ap = found_interface.accesspoint
        for ip_address in alternatives:
            interface = EthernetNetworkInterface.objects.filter(accesspoint=ap,
                                                                addresses__address=ip_address)
            if not interface:
                interface = EthernetNetworkInterface.objects.create(accesspoint=ap)
                address_object = NetworkInterfaceAddress.create_with_ipaddress(
                    interface,
                    ipaddress.ip_interface("{}/{:d}".format(ip_address, NETMASK_PREFIXLEN)))
                logging.info("Created new NetworkInterface %s", ip_address)
                interface.save()
                address_object.save()


def import_routes_from_olsr(txtinfo_url="http://localhost:2006"):
    url = "%s/%s" % (txtinfo_url.rstrip("/"), "all")
    olsr_data = urllib.request.urlopen(url).read().decode("ascii")
    import_routes_from_olsr_data(olsr_data)


@transaction.atomic
def import_routes_from_olsr_data(content):
    topology_lines = content.splitlines()
    tables = _txtinfo_parser(topology_lines, ("routes", "hna", "topology", "mid", "links"))
    # first "MID" then "Routes" - otherwise secondary IPs are used for nodes
    parse_hna_and_mid_for_alternatives(tables["mid"], tables["hna"])
    parse_topology_for_links(tables["topology"], tables["links"])


if __name__ == "__main__":
    import_routes_from_olsr()
    nodes = AccessPoint.objects()
    for node in nodes:
        print(repr(node))
    print(len(nodes))
