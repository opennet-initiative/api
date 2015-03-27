""" parse the content of an ondataservice database.
    This sqlite database contains two tables: "nodes" and "ifaces".
    The resulting information can be attached to Node objects.
"""

import sys
import re
import time
import sqlite3

import oni_model.models


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


def _parse_nodes_data(conn, max_age_seconds=3600):
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
    # add network interfaces
    ifaces_columns = _get_table_meta(conn, "ifaces")
    query = conn.execute("SELECT * FROM ifaces WHERE db_update >= %d" % min_epoch)
    for row in query.fetchall():
        data = get_row_dict(row, ifaces_columns)
        import_network_interface(data)


# "data" ist ein Dictionary mit den Inhalten aus der ondataservice-sqlite-Datenbank
def import_accesspoint(data):
    main_ip = data["on_olsrd_mainip"]
    if not main_ip:
        return
    node, created = oni_model.models.AccessPoint.objects.get_or_create(main_ip=main_ip)
    mapping = {
        "sys_os_type": "sys_os_type",
        "sys_os_name": "sys_os_name",
    }
    for key_from, key_to in mapping.items():
        setattr(node, data[key_from])
    node.save()


# "data" ist ein Dictionary mit den Inhalten aus der ondataservice-sqlite-Datenbank
def import_network_interface(data):
    main_ip = data["mainip"]
    node = oni_model.models.AccessPoint.objects.get(main_ip=main_ip)
    if not node:
        # wir legen keine Netzwerk-Interfaces fuer APs an, die noch nicht in der Datenbank sind
        return
    # Uebertragung von sqlite-Eintraegen in unser Modell
    mapping = {
        "if_name": "if_name",
        "if_type_bridge": "if_is_bridge",
        "if_type_bridgedif": "if_is_bridged",
        "if_hwaddress": "if_hwaddress",
        "ip_label": "ip_label",
        "ip_address": "ip_address",
        "ip_broadcast": "ip_broadcast",
        "on_networks": "opennet_networks",
        "on_zones": "opennet_firewall_zones",
        "on_olsr": "olsr_enabled",
        "dhcp_start": "dhcp_start",
        "dhcp_limit": "dhcp_limit",
        "dhcp_leasetime": "dhcp_leasetime",
        "dhcp_fwd": "dhcp_forward",
        "ifstat_collisions": "ifstat_collisions",
        "ifstat_rx_compressed": "ifstat_rx_compressed",
        "ifstat_rx_errors": "ifstat_rx_errors",
        "ifstat_rx_length_errors": "ifstat_rx_length_errors",
        "ifstat_rx_packets": "ifstat_rx_packets",
        "ifstat_tx_carrier_errors": "ifstat_tx_carrier_errors",
        "ifstat_tx_errors": "ifstat_tx_errors",
        "ifstat_tx_packets": "ifstat_tx_packets",
        "ifstat_multicast": "ifstat_multicast",
        "ifstat_rx_crc_errors": "ifstat_rx_crc_errors",
        "ifstat_rx_fifo_errors": "ifstat_rx_fifo_errors",
        "ifstat_rx_missed_errors": "ifstat_rx_missed_errors",
        "ifstat_tx_aborted_errors": "ifstat_tx_aborted_errors",
        "ifstat_tx_compressed": "ifstat_tx_compressed",
        "ifstat_tx_fifo_errors": "ifstat_tx_fifo_errors",
        "ifstat_tx_window_errors": "ifstat_tx_window_errors",
        "ifstat_rx_bytes": "ifstat_rx_bytes",
        "ifstat_rx_dropped": "ifstat_rx_dropped",
        "ifstat_rx_frame_errors": "ifstat_rx_frame_errors",
        "ifstat_rx_over_errors": "ifstat_rx_over_errors",
        "ifstat_tx_bytes": "ifstat_tx_bytes",
        "ifstat_tx_dropped": "ifstat_tx_dropped",
        "ifstat_tx_heart": "ifstat_tx_heart",
    }
    # wir verwenden fuer wlan-Interfaces eine separate Klasse und weitere Attribute fuer wifi-Interfaces
    if data["ssid"]:
        interface, created = oni_model.models.WifiNetworkInterface.objects.get_or_create(access_point=node, ifname=data["ifname"])
        mapping.update({
            "wlan_essid": "wifi_ssid",
            "wlan_ap": "wifi_bssid",
            "wlan_type": "wifi_driver",
            "wlan_hwmode": "wifi_hwmode",
            "wlan_mode": "wifi_mode",
            "wlan_channel": "wifi_channel",
            "wlan_freq": "wifi_freq",
            "wlan_txpower": "wifi_signal",
            "wlan_signal": "wifi_signal",
            "wlan_noise": "wifi_noise",
            "wlan_bitrate": "wifi_bitrate",
            "wlan_crypt": "wifi_crypt",
            "wlan_vaps": "wifi_vaps_enabled",
        })
    else:
        interface, created = oni_model.models.EthernetNetworkInterface.objects.get_or_create(access_point=node, ifname=data["ifname"])
    for key_from, key_to in mapping.items():
        setattr(interface, data[key_from])
    interface.save()


def import_from_ondataservice(db_file="/var/run/olsrd/ondataservice.db"):
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.OperationalError as err_msg:
        print("Failed to open ondataservice database (%s): %s" % (db_file, err_msg), file=sys.stderr)
    else:
        _parse_nodes_data(conn)
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No database given - exit.", file=sys.stderr)
    mesh = parse_ondataservice(db_file=sys.argv[1])
    for a in mesh.nodes:
        print(repr(a))

