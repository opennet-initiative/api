""" apply opennet specific filters and interpretations to a mesh
"""
import re

import ipaddress as ipaddr


OUR_NETWORKS = ['192.168.0.0/16']


def is_our_network(network):
    network = ipaddr.IPv4Network(network)
    for filter_net_string in OUR_NETWORKS:
        filter_net = ipaddr.IPv4Network(filter_net_string)
        if network in filter_net:
            return True
    return False


def parse_node_ip(address):
    """ Parse strings with full IP address or APx or APx.y values.
        Return ipaddr.IPAddress 
    """
    if isinstance(address, ipaddr.IPv4Address):
        return address
    elif isinstance(address, ipaddr.IPv4Network):
        if address.numhosts == 1:
            # a single-host network
            return address[0]
        else:
            raise TypeError("Network given instead of an address: %s" % address)
    elif isinstance(address, str) and address.upper().startswith("AP"):
        # remove "AP" prefix
        # something like "1.89" or "89" should remain
        ap_name = address[2:]
        # we tolerate different separators (-_.) and strip whitespace before and after
        spaced = re.sub(r"[-_.]", " ", ap_name).strip()
        # parse octet integers from the string
        try:
            octets = [int(value) for value in spaced.split()]
        except ValueError:
            raise ValueError("Failed to parse numbers in AP name: %s" % ap_name)
        if len(octets) == 1:
            # use the default subnetwork (192.168.1.y) if only one octet was given
            default_subnet = 1
            octets.insert(0, default_subnet)
        if len(octets) != 2:
            raise ValueError("Invalid number of octets parsed - only two were expected: %s" % ap_name)
        else:
            node_ip = "192.168.%d.%d" % tuple(octets)
            return ipaddr.IPv4Address(node_ip)
    else:
        # parse an IP address string
        try:
            return ipaddr.IPv4Address(address)
        except ValueError:
            pass
        # parse a network string
        try:
            network = ipaddr.IPv4Network(address)
            if network.num_addresses == 1:
                return network[0]
        except ValueError:
            pass
        # give up
        raise ValueError("Failed to parse a node address: %s" % address)


def get_accesspoint_pretty_name(node):
    # remove nodes which do not contain an address within our networks
    # and add opennet-specific names to remaining nodes
    matching_addresses = [address for address in node["addresses"] if is_our_network(address)]
    if matching_addresses:
        main_ip = str(matching_addresses[0])
        last_octets = main_ip.split(".")[-2:]
        return "AP%s.%s" % tuple(last_octets)
    else:
        return None

