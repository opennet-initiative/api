import ipaddr
import calendar
import datetime


__MESH_STORE = []

def get_mesh():
    if not __MESH_STORE:
        __MESH_STORE.append(Mesh())
    return __MESH_STORE[0]


def get_nodes_key(nodes):
    node_ips = [str(node["ip"]) for node in nodes]
    return tuple(sorted(node_ips))


def get_address(address):
    if isinstance(address, ipaddr._BaseIP):
        return address
    # simple address without netmask?
    try:
        return ipaddr.IPAddress(address)
    except ValueError as original_exception:
        pass
    # network mask with a single host (.../32)
    try:
        network = ipaddr.IPNetwork(address)
    except ValueError:
        raise original_exception
    if network.numhosts == 1:
        return network[0]
    else:
        raise original_exception


class NodeCountError(TypeError):
    pass


class AttributableObject(object):

    _FLAG_BLACKLIST = ["mesh"]

    def get_flags(self):
        """ collect all public non-callable items in the namespace of an object """
        result = {}
        for key in dir(self):
            if key in self._FLAG_BLACKLIST:
                continue
            if key.startswith("_"):
                continue
            item = getattr(self, key)
            if not callable(item):
                result[key] = item
        return result

    def touch(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.datetime.now()
        self.alive_timestamp = timestamp

    def is_alive(self, max_age_seconds=60):
        now = datetime.datetime.now()
        max_age = datetime.timedelta(seconds=max_age_seconds)
        try:
            return now - self.alive_timestamp <= max_age
        except AttributeError:
            return False

    def get_timestamp(self):
        try:
            return self.alive_timestamp
        except AttributeError:
            return None

    def get_timestamp_epoch(self):
        timestamp = self.get_timestamp()
        if timestamp:
            return calendar.timegm(timestamp.utctimetuple())
        else:
            return None


class Node(AttributableObject):

    def __init__(self, mesh, main_ip):
        self._FLAG_BLACKLIST.append("addresses")
        self.mesh = mesh
        self.addresses = (get_address(main_ip), )

    def get_links(self):
        return [link for link in self.mesh.links if self in link.nodes]

    def get_clusters(self):
        return [cluster for cluster in self.mesh.clusters if self in cluster.nodes]

    def add_address(self, address):
        address = get_address(address)
        # verify that there are no duplicates
        assert not any([address in node.addresses for node in self.mesh.nodes if not node is self])
        if not address in self.addresses:
            self.addresses = tuple(self.addresses + (address, ))

    def __str__(self):
        return str(self.addresses[0])

    def __repr__(self):
        main_ip = str(self.addresses[0])
        description = [main_ip]
        description.extend([("%s='%s'" % (key, value)).decode("UTF-8") for key, value in self.get_flags().iteritems()])
        description_string = ", ".join(description).encode("UTF-8")
        return "Node(%s)" % description_string


class Link(AttributableObject):

    def __init__(self, mesh, nodes):
        self._FLAG_BLACKLIST.append("nodes")
        self.mesh = mesh
        assert self.__verify_nodes_count(nodes)
        assert all([isinstance(node, Node) for node in nodes])
        self.nodes = tuple(nodes)

    def __verify_nodes_count(self, nodes):
        return len(nodes) == 2

    def remove_node(self, node):
        # this is quite pointless for links - but useful for clusters
        new_nodes = list(self.nodes)
        new_nodes.remove(node)
        if not self.__verify_nodes_count(new_nodes):
            raise NodeCountError("Too few nodes for a %s: %d" % (self.__class__.__name__, len(new_nodes)))
        self.nodes = new_nodes

    def get_others(self, node):
        if not node in self.nodes:
            raise ValueError("The given node (%s) is not connected to this object (%s)" % (node, self))
        return [one_node for one_node in self.nodes if not one_node is node]

    def __str__(self):
        nodes_string = "[%s, %s]" % (str(self.nodes[0]), str(self.nodes[1]))
        return "%s %s" % (self.nodes, self.get_flags())

    def __repr__(self):
        description = ["(%s, %s)" % self.nodes]
        description.extend(["%s='%s'" % (key, value) for key, value in self.get_flags().iteritems()])
        description_string = ", ".join(description)
        return "%s(%s)" % (self.__class__.__name__, description_string)


class Cluster(Link):

    def __verify_nodes_count(self, nodes):
        return len(nodes) > 2


class Mesh(object):

    def __init__(self):
        self.nodes = []
        self.links = []
        self.clusters = []

    def get_node(self, ip):
        node = self._find_node(ip)
        if node is None:
            # we did not find a Node - create a new one
            new_node = Node(self, ip)
            self.nodes.append(new_node)
            return new_node
        else:
            return node

    def has_node(self, ip):
        return not self._find_node(ip) is None

    def _find_node(self, ip):
        address = get_address(ip)
        # look for a node associated with this address
        for node in self.nodes:
            if address in node.addresses:
                return node
        return None

    def _get_list_match(self, nodes, item_list, factory):
        nodes = [self.get_node(node) for node in nodes]
        # check if all nodes are part of one item
        for item in item_list:
            for node in nodes:
                if not node in item.nodes:
                    break
            else:
                return item
        # we did not find a match - create a new object
        new_item = factory(self, nodes)
        item_list.append(new_item)
        return new_item

    def get_link(self, nodes):
        return self._get_list_match(nodes, self.links, Link)

    def get_cluster(self, nodes):
        return self._get_list_match(nodes, self.clusters, Cluster)

    def remove_node(self, node):
        # remove node from associated clusters (this will usually remove them, as well)
        for link in node.get_links():
            try:
                link.remove_node(node)
            except NodeCountError:
                self.links.remove(link)
        # remove node from associated clusters
        for cluster in node.get_clusters():
            try:
                cluster.remove_node(node)
            except NodeCountError:
                self.cluster.remove(link)
        self.nodes.remove(node)

