""" parse the content of an ondataservice database.
    This sqlite database contains two tables: "nodes" and "ifaces".
    The resulting information can be attached to Node objects.
"""

import sys
import re
import time
import sqlite3

import elements


COLUMN_BLACKLISTS = {
        "nodes": [r"^db_", "mainip$"],
        "ifaces": [r"^db_", "mainip$"],
}


def _get_table_meta(conn, table):
    """ Retrieve meta informations about the columns of a table.
        Each column is represented by a tuple of four values:
            - index
            - name
            - type
            - default value
        @type conn: sqlite3.Connection
        @param conn: an open sql connection
        @type table: string
        @param table: name of a table
        @rtype: list of strings
        @return: list of column names
    """
    columns = conn.execute("PRAGMA table_info(%s)" % table)
    return [col[1] for col in columns.fetchall()]


def _parse_nodes_data(mesh, conn, max_age_seconds=300, create_new=True):
    """ Retrieve all node information from the "nodes" table.
        @type mesh: elements.Mesh
        @param mesh: the mesh network to be updated
        @type conn: sqlite3.Connection
        @param conn: an open sql connection
        @type max_age: int
        @param max_age: maximum age of a table entry in seconds
        @type create_new: bool
        @param create_new: create new nodes in the mesh?
        @rtype: elements.Mesh
        @return: the mesh with updated nodes
    """
    nodes_columns = _get_table_meta(conn, "nodes")
    def get_row_dict(row, columns):
        result = {}
        for key, value in zip(columns, row):
            result[key] = value
        return result
    min_epoch = time.time() - max_age_seconds
    # add node tags
    query = conn.execute("SELECT * FROM nodes WHERE db_update >= %d" % min_epoch)
    for row in query.fetchall():
        data = get_row_dict(row, nodes_columns)
        main_ip = data["on_olsrd_mainip"]
        if main_ip and (create_new or mesh.has_node(main_ip)):
            node = mesh.get_node(main_ip)
            for key in nodes_columns:
                if any([re.search(pattern, key) for pattern in COLUMN_BLACKLISTS["nodes"]]):
                    continue
                # key is not blacklisted
                setattr(node, key, data[key])
    # add network interfaces
    ifaces_columns = _get_table_meta(conn, "ifaces")
    query = conn.execute("SELECT * FROM ifaces WHERE db_update >= %d" % min_epoch)
    for row in query.fetchall():
        data = get_row_dict(row, ifaces_columns)
        main_ip = data["mainip"]
        if not create_new and not mesh.has_node(main_ip):
            continue
        node = mesh.get_node(main_ip)
        if not hasattr(node, "links"):
            node.links = []
        link = {}
        for key in ifaces_columns:
            if any([re.search(pattern, key) for pattern in COLUMN_BLACKLISTS["ifaces"]]):
                continue
            # key is not blacklisted
            link[key] = data[key]
        node.links.append(link)


def parse_ondataservice(mesh=None, db_file="/var/run/olsrd/ondataservice.db", max_age_seconds=300, create_new=True):
    if mesh is None:
        mesh = elements.get_mesh()
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.OperationalError as err_msg:
        print("Failed to open ondataservice database (%s): %s" % (db_file, err_msg), file=sys.stderr)
    else:
        _parse_nodes_data(mesh, conn, max_age_seconds=max_age_seconds, create_new=create_new)
        conn.close()
    return mesh


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No database given - exit.", file=sys.stderr)
    mesh = parse_ondataservice(db_file=sys.argv[1])
    for a in mesh.nodes:
        print(repr(a))
    
