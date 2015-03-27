import sys
import json
import requests

import elements
import import_olsr
import import_wiki
import opennet


OPENWIFIMAP_API_URL = "http://api.openwifimap.net"
DOMAIN = "oni"


def _send_data(endpoint, data, api_url=OPENWIFIMAP_API_URL):
    url = "%s/%s" % (OPENWIFIMAP_API_URL.rstrip("/"), endpoint)
    req = requests.put(url, data=data)
    req_ok = 200 <= req.status_code < 300
    return req_ok, req.text


def _node2json(node):
    data = {}
    data["type"] = "node"
    name = getattr(node, "name", str(node.addresses[0]))
    data["hostname"] = name
    if getattr(node, "lat", None):
        data["latitude"] = node.lat
    if getattr(node, "lon", None):
        data["longitude"] = node.lon
    links = []
    for link in node.get_links():
        partner = [other for other in link.nodes if not node is other][0]
        link_data = {}
        link_data["id"] = _get_node_id(other)
        # avoid divide-by-zero
        if getattr(link, "cost", 0) > 0:
            link_data["quality"] = 1.0 / link.cost
        links.append(link_data)
    if links:
        data["links"] = links
    data["updateInterval"] = 10000
    return json.dumps(data)


def _get_node_id(node):
    name = getattr(node, "name", str(node.addresses[0]))
    return ".".join((DOMAIN, name))


def push_to_api(mesh, api_url=OPENWIFIMAP_API_URL):
    for node in mesh.nodes:
        if node.is_alive() and "lat" in node.get_flags() and "lon" in node.get_flags():
            json_text = _node2json(node)
            node_id = _get_node_id(node)
            status, text = _send_data("update_node/%s" % node_id, json_text, api_url=api_url)
            if not status:
                print(node.name, text.strip(), file=sys.stderr)


if __name__ == "__main__":
    mesh = import_olsr.parse_olsr_topology()
    import_wiki.parse_wiki_nodelist(mesh)
    opennet.apply_opennet(mesh)
    for node in mesh.nodes:
        if node.is_alive() and "lat" in node.get_flags() and "lon" in node.get_flags():
            json_text = _node2json(node)
            node_id = _get_node_id(node)
            status, text = _send_data("update_node/%s" % node_id, json_text)
            if not status:
                print(node.name, text.strip())

