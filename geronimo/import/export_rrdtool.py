import os
import rrdtool

import export_pygraph


DEFAULT_INTERVAL = 60


def _get_rrd_filename_for_node(parent_dir, node):
    node_name = str(node)
    return _get_rrd_filename(parent_dir, node_name, "node")


def _get_rrd_filename_for_link(parent_dir, link):
    # generate a unique undirected name
    node_addresses = [node.addresses[0] for node in link.nodes]
    node_addresses.sort()
    link_name = "-".join([str(address) for address in node_addresses])
    return _get_rrd_filename(parent_dir, link_name, "link")


def _get_rrd_filename(parent_dir, name, prefix):
    path = os.path.join(parent_dir, prefix, "%s.rrd" % name)
    path = os.path.abspath(os.path.expanduser(path))
    return path


def _get_ugw_cost_and_links(mesh, node):
    ugw_cost = []
    graph = export_pygraph.NetworkGraph(mesh)
    for ugw in mesh.nodes:
        if not getattr(ugw, "ugw", False):
            continue
        if ugw is node:
            # the node itself is a UGW
            return ugw, 1.0, []
        try:
            cost, links = graph.get_shortest_path(node, ugw)
            ugw_cost.append((ugw, cost, links))
        except KeyError:
            continue
    if not ugw_cost:
        raise KeyError("No connection found between node %s and a gateway." % node)
    ugw_cost.sort(key=lambda item: item[1])
    return ugw_cost[0]


def _create_rrd(filename, keys):
    options = []
    # create new data series
    for key in keys:
        options.append("DS:%s:GAUGE:%d:0:1" % (key, 3 * DEFAULT_INTERVAL))
    # update schema
    cumulated = 0
    factors = (1, 6, 24, 24 * 7, 24 * 30, 24 * 365, 24 * 365 * 10)
    for key in keys:
        for func in ("AVERAGE", "MIN", "MAX"):
            rows = 24 * 60
            for index, factor in enumerate(factors):
                cumulated += rows / factor
                options.append("RRA:%s:0.5:%d:%d" % (func, factor, cumulated))
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    rrdtool.create(filename, "--step", str(DEFAULT_INTERVAL), *options)


def _update_rrd(filename, value_dict, timestamp):
    if not os.path.exists(filename):
        _create_rrd(filename, list(value_dict.keys()))
    # sort the templates and sort the values
    keys = []
    values = [str(timestamp)]
    for key, value in value_dict.items():
        keys.append(key)
        values.append(str(value))
    key_string = ":".join(keys)
    value_string = ":".join(values)
    rrdtool.update(filename, "--template", key_string, value_string)


def update_rrd_database(mesh, parent_dir):
    for node in mesh.nodes:
        try:
            ugw, cost, links = _get_ugw_cost_and_links(mesh, node)
        except KeyError:
            continue
        datasets = {}
        try:
            worst_hop_distance = max([1.0] + [link.cost for link in links])
        except KeyError:
            for key in ("closest_ugw_worst_hop", "closest_ugw_avg_hop", "closest_ugw_minus_hop"):
                datasets[key] = 1.0
            continue
        datasets["NextUgwWorstHop"] = worst_hop_distance
        datasets["NextUgwAvgHop"] = 1.0 if not links else (float(cost) / len(links))
        datasets["NextUgwMinusHop"] = cost - len(links)
        timestamp = node.get_timestamp_epoch()
        if not timestamp:
            continue
        rrd_filename = _get_rrd_filename_for_node(parent_dir, node)
        _update_rrd(rrd_filename, datasets, timestamp)
    for link in mesh.links:
        rrd_filename = _get_rrd_filename_for_link(parent_dir, link)
        timestamps = [node.get_timestamp_epoch() for node in link.nodes if node.get_timestamp_epoch()]
        if not timestamps:
            continue
        _update_rrd(rrd_filename, {"cost": link.cost}, min(timestamps))


if __name__ == "__main__":
    import sys
    import os
    import import_olsr
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.getcwd()
    mesh = import_olsr.parse_olsr_topology()
    update_rrd_database(mesh, base_dir)

