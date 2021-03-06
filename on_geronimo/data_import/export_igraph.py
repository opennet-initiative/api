import igraph


def generate_igraph(mesh):
    graph = igraph.Graph()
    # create blank edges and vertices
    graph.add_vertices(len(mesh.nodes))
    # import nodes
    for index, node in enumerate(mesh.nodes):
        vertex = graph.vs[index]
        # use the main IP as the name by default (can be overwritten below)
        vertex["name"] = str(node.addresses[0])
        # apply all flags to the vertex
        for key, value in node.get_flags().items():
            vertex[key] = value
    # import links
    for index, link in enumerate(mesh.links):
        node_ids = [mesh.nodes.index(node) for node in link.nodes]
        graph.add_edges([node_ids])
        edge = graph.es[index]
        # apply all flags to the vertex
        for key, value in link.get_flags().items():
            edge[key] = value
    return graph


if __name__ == "__main__":
    import opennet
    mesh = opennet.import_opennet_mesh()
    graph = generate_igraph(mesh)
    print(graph)
    igraph.plot(graph, "output.png")
