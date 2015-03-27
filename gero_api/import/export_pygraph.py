import pygraph.classes.graph
import pygraph.algorithms.minmax


class NetworkGraph(object):

    def __init__(self, mesh):
        self.mesh = mesh
        graph = pygraph.classes.graph.graph()
        graph.add_nodes(list(self.mesh.nodes))
        for link in self.mesh.links:
            node1, node2 = link.nodes
            graph.add_edge((node1, node2), wt=link.cost)
        self._graph = graph

    def get_shortest_path(self, node1, node2):
        """ Calculate the shortest path between two nodes.
            Returns a tuple of distance and hops (elements.Link) between the nodes.
            Raise KeyError if the given nodes are not connected.
        """
        spanning_tree, graph_ordering = pygraph.algorithms.minmax.shortest_path(self._graph, node2)
        if not node1 in graph_ordering:
            raise KeyError("No connection between %s and %s." % (node1, node2))
        current = node1
        links = []
        while not spanning_tree[current] is None:
            next_node = spanning_tree[current]
            link = self.mesh.get_link((current, next_node))
            links.append(link)
            current = next_node
        return graph_ordering[node1], links


if __name__ == "__main__":
    import opennet
    mesh = opennet.import_opennet_mesh()
    graph = NetworkGraph(self.mesh)
    node1, node2 = mesh.nodes[0], mesh.nodes[4]
    print(graph.get_shortest_path(node1, node2))

