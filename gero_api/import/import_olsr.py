import urllib.request, urllib.parse, urllib.error
import ipaddr
import elements


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


def parse_routes_for_nodes(mesh, routes_table):
    for destination, via, metric, etx, interface in routes_table:
        node = mesh.get_node(destination)
        # attach a timestamp
        node.touch()


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


def parse_hna_for_ugw(mesh, hna_table):
    for destination, gateway in hna_table:
        gateway_node = mesh.get_node(gateway)
        destination = ipaddr.IPNetwork(destination)
        if destination.numhosts == 1:
            gateway_node.ugw = destination[0]


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
    parse_mid_for_alternatives(mesh, tables["mid"])
    parse_routes_for_nodes(mesh, tables["routes"])
    parse_topology_for_links(mesh, tables["topology"], tables["links"])
    parse_hna_for_ugw(mesh, tables["hna"])
    return mesh


if __name__ == "__main__":
    mesh = parse_olsr_topology()
    for item in mesh.links:
        print(repr(item))

