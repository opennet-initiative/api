""" apply opennet specific filters and interpretations to a mesh
"""
import re

import ipaddr


OUR_NETWORKS = ['192.168.0.0/16']


def is_our_network(network):
    network = ipaddr.IPNetwork(network)
    for filter_net_string in OUR_NETWORKS:
        filter_net = ipaddr.IPNetwork(filter_net_string)
        if network in filter_net:
            return True
    return False


def parse_node_ip(address):
    """ Parse strings with full IP address or APx or APx.y values.
        Return ipaddr.IPAddress 
    """
    if isinstance(address, ipaddr._BaseIP):
        return address
    elif isinstance(address, ipaddr._BaseNet):
        if address.numhosts == 1:
            # a single-host network
            return address[0]
        else:
            raise TypeError("Network given instead of an address: %s" % address)
    elif isinstance(address, basestring) and address.upper().startswith("AP"):
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
            return ipaddr.IPAddress(node_ip)
    else:
        # parse an IP address string
        try:
            return ipaddr.IPAddress(address)
        except ValueError:
            pass
        # parse a network string
        try:
            network = ipaddr.IPNetwork(address)
            if network.numhosts == 1:
                return network[0]
        except ValueError:
            pass
        # give up
        raise ValueError("Failed to parse a node address: %s" % address)


def apply_opennet(mesh):
    removal_list = []
    # remove nodes which do not contain an address within our networks
    # and add opennet-specific names to remaining nodes
    for node in mesh.nodes:
        matching_addresses = [address for address in node.addresses if is_our_network(address)]
        if matching_addresses:
            main_ip = str(matching_addresses[0])
            last_octets = main_ip.split(".")[-2:]
            name = "AP%s.%s" % tuple(last_octets)
            node.name = name
        else:
            removal_list.append(node)
    for node in removal_list:
        mesh.remove_node(node)
 

def import_opennet_mesh(mesh=None):
    import import_olsr
    import import_wiki
    import import_ondataservice
    mesh = import_olsr.parse_olsr_topology(mesh)
    import_wiki.parse_wiki_nodelist(mesh)
    apply_opennet(mesh)
    import_ondataservice.parse_ondataservice(mesh)
    return mesh


if __name__ == "__main__":
    mesh = import_opennet_mesh()
    for item in mesh.nodes:
        print repr(item)

