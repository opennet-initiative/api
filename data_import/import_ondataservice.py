""" parse the content of an ondataservice database.
    This sqlite database contains two tables: "nodes" and "ifaces".
    The resulting information can be attached to Node objects.

    documentation: https://wiki.opennet-initiative.de/wiki/Ondataservice
"""

import sys
import re
import time
import sqlite3
import datetime

from oni_model.models import AccessPoint, EthernetNetworkInterface, WifiNetworkInterfaceAttributes
from django.db import transaction


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


def _parse_nodes_data(conn):
    nodes_columns = _get_table_meta(conn, "nodes")
    def get_row_dict(row, columns):
        result = {}
        for key, value in zip(columns, row):
            result[key] = value
        return result
    # add node tags
    for node in conn.execute("SELECT * FROM nodes").fetchall():
        data = get_row_dict(node, nodes_columns)
        try:
            import_accesspoint(data)
        except ValueError:
            print("Failed to update node %s: %s" % (node, data))
            raise
    # add network interfaces
    ifaces_columns = _get_table_meta(conn, "ifaces")
    for iface in conn.execute("SELECT * FROM ifaces").fetchall():
        data = get_row_dict(iface, ifaces_columns)
        try:
            import_network_interface(data)
        except ValueError:
            print("Failed to update interface %s: %s" % (iface, data))
            raise


def _update_value(target, attribute, raw_value):
    target_attr = getattr(target, attribute)
    if attribute.startswith("ifstat_"):
        # Standard-Wert Null fuer Interface-Statistiken
        value = int(raw_value) if raw_value else 0
    elif (attribute in ("wifi_bitrate", "wifi_signal", "wifi_noise")) and (raw_value == "unknown"):
        value = 0
    elif (attribute in ("wifi_signal", "wifi_noise", "wifi_freq", "wifi_channel", "device_memory_available", "device_memory_free")) and (raw_value == ""):
        value = 0
    elif (attribute in ("wifi_freq", "wifi_channel")) and ("unknown" in raw_value):
        # Parse-Fehler in der Firmware (bis v0.5.2) ausgleichen
        value = 0
    elif attribute in ("dhcp_range_start", "dhcp_range_limit"):
        # die DHCP-Werte tragen "null=True" - daher sind sie nicht als Integer erkennbar
        value = int(raw_value) if raw_value else None
    elif attribute.endswith("_timestamp"):
        value = datetime.date.fromtimestamp(int(raw_value)) if raw_value else None
    elif attribute == "system_uptime":
        # in 0.9-ON5 enthaelt uptime eine textuelle Ausgabe (z.B.: "6 days, 18:18" oder "21:01")
        days_text_regex = r"(?:(?P<days>[0-9]+) days?,)? *(?P<hours>[0-9]{1,2}):(?P<minutes>[0-9]{2})$"
        match = re.match(days_text_regex, raw_value)
        if match:
            numbers = {key: int(text or 0) for key, text in match.groupdict().items()}
            value = float(60 * (numbers["minutes"] + 60 * (numbers["hours"] + 24 * numbers["days"])))
        else:
            # TODO: ab Django 1.8 gibt es DurationField - fuer timedelta
            #value = datetime.timedelta(seconds=float(raw_value))
            value = float(raw_value) if raw_value else None
    elif attribute == "opennet_services_sorting":
        # wir nennen die "metric"-Sortierung heute "hop"
        value = "hop" if raw_value == "metric" else raw_value
    elif attribute == "wifi_mode":
        value = {
                "Master": "master",
                "Managed": "client",
                "Client": "client",
                "Ad-Hoc": "adhoc",
                "AdHoc": "adhoc",
                "Monitor": "monitor",
            }[raw_value]
    elif attribute == "wifi_crypt":
        value = {
                "WEP Open System (NONE)": "WEP",
                "WPA2 PSK (CCMP)": "WPA2-PSK",
                "mixed WPA/WPA2 PSK (TKIP)": "WPA2-PSK",
                "WPA PSK (CCMP)": "WPA-PSK",
                "unknown": "Plain",
                "open": "Plain",
                "none": "Plain",
                "None": "Plain",
                "": "Plain",
            }[raw_value.strip()]
    elif (attribute == "wifi_hwmode") and raw_value.startswith("802.11"):
        # beim hwmode sortieren verschiedene APs die Suffixe in unterschiedlicher Reihenfolge
        # verwandle "802.11na" in "802.11an"
        sorted_suffix = sorted(raw_value[6:])
        value = "802.11" + "".join(sorted_suffix)
    elif type(target_attr) is int:
        # Standard-Wert None fuer Interface-Statistiken
        value = float(raw_value) if raw_value else None
    elif (type(target_attr) is bool) \
            or attribute.endswith("_enabled") \
            or attribute.endswith("_connected") \
            or attribute.endswith("_running"):
        # ein paar der bool-Werte sind als String definiert
        value = ((raw_value == "1") or (raw_value == 1))
    else:
        value = str(raw_value)
    setattr(target, attribute, value)


def _parse_dhcp_leasetime_seconds(text):
    if text.endswith("h"):
        return int(text[:-1]) * 3600
    elif text.endswith("m"):
        return int(text[:-1]) * 60
    elif text.endswith("s"):
        return int(text[:-1])
    else:
        return None


# "data" ist ein Dictionary mit den Inhalten aus der ondataservice-sqlite-Datenbank
def import_accesspoint(data):
    main_ip = data["on_olsrd_mainip"]
    if not main_ip:
        return
    node, created = AccessPoint.objects.get_or_create(main_ip=main_ip)
    for key_from, key_to in {
                "sys_board": "device_board",
                "sys_os_arc": "device_architecture",
                "sys_cpu": "device_cpu",
                "sys_mem": "device_memory_available",
                "sys_free": "device_memory_free",

                "sys_ver": "system_kernel",
                "sys_watchdog": "system_watchdog_enabled",
                "sys_uptime": "system_uptime",

                "sys_os_type": "firmware_type",
                "sys_os_name": "firmware_release_name",
                "sys_os_rel": "firmware_release_version",
                "sys_os_ver": "firmware_build",
                "sys_os_insttime": "firmware_install_timestamp",

                "on_core_ver": "opennet_version",
                "on_core_insttime": "opennet_install_timestamp",
                "on_packages": "opennet_packages",
                "on_id": "opennet_id",
                "on_olsrd_status": "olsrd_running",
                "on_olsrd_mainip": "olsrd_main_ip",

                "on_wifidog_status": "opennet_captive_portal_enabled",
                "on_wifidog_id": "opennet_captive_portal_name",

                "on_vpn_cn": "opennet_certificate_cn",
                "on_vpn_status": "opennet_vpn_internet_enabled",
                "on_vpn_gw": "opennet_vpn_internet_connections",
                "on_vpn_autosearch": "opennet_vpn_internet_autosearch",
                "on_vpn_sort": "opennet_services_sorting",
                "on_vpn_gws": "opennet_vpn_internet_gateways",
                "on_vpn_blist": "opennet_vpn_internet_blacklist",

                "on_ugw_status": "opennet_service_relay_connected",
                "on_ugw_enabled": "opennet_service_relay_enabled",
                "on_ugw_tunnel": "opennet_vpn_mesh_connected",
                "on_ugw_connected": "opennet_vpn_mesh_connections",
                "on_ugw_presetips": "opennet_vpn_mesh_gateways",
                "on_ugw_presetnames": "opennet_vpn_mesh_gateway_names",
            }.items():
        _update_value(node, key_to, data[key_from])
    # load-Werte
    if data["sys_load"]:
        for minutes, value in zip((1, 5, 15), data["sys_load"].split()):
            # machnaml haengt an einer Zeit-Angabe noch ein Komma (z.B.: "1.53,")
            value = value.strip(",")
            setattr(node, "system_load_%dmin" % minutes, float(value))
    node.save()


# "data" ist ein Dictionary mit den Inhalten aus der ondataservice-sqlite-Datenbank
def import_network_interface(data):
    main_ip = data["mainip"]
    try:
        node = AccessPoint.objects.get(main_ip=main_ip)
    except AccessPoint.DoesNotExist:
        # wir legen keine Netzwerk-Interfaces fuer APs an, die noch nicht in der Datenbank sind
        return
    # wir verwenden fuer wlan-Interfaces eine separate Klasse und weitere Attribute fuer wifi-Interfaces
    try:
        interface = EthernetNetworkInterface.objects.get(access_point=node, if_name=data["if_name"])
    except EthernetNetworkInterface.DoesNotExist:
        interface = EthernetNetworkInterface.objects.create(access_point=node, ip_address=data["ip_addr"])
    # Uebertragung von sqlite-Eintraegen in unser Modell
    for key_from, key_to in {
                "if_name": "if_name",
                "if_type_bridge": "if_is_bridge",
                "if_type_bridgedif": "if_is_bridged",
                "if_hwaddr": "if_hwaddress",
                "ip_label": "ip_label",
                "ip_addr": "ip_address",
                "ip_broadcast": "ip_broadcast",
                "on_networks": "opennet_networks",
                "on_zones": "opennet_firewall_zones",
                "on_olsr": "olsr_enabled",
                "dhcp_start": "dhcp_range_start",
                "dhcp_limit": "dhcp_range_limit",
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
                "ifstat_tx_heartbeat_errors": "ifstat_tx_heartbeat_errors",
            }.items():
        _update_value(interface, key_to, data[key_from])
        interface.dhcp_leasetime = _parse_dhcp_leasetime_seconds(data["dhcp_leasetime"])
    interface.save()
    if data["wlan_essid"]:
        wifi_attributes, created = WifiNetworkInterfaceAttributes.objects.get_or_create(interface=interface)
        for key_from, key_to in {
                    "wlan_essid": "wifi_ssid",
                    "wlan_apmac": "wifi_bssid",
                    "wlan_type": "wifi_driver",
                    "wlan_channel": "wifi_channel",
                    "wlan_crypt": "wifi_crypt",
                    "wlan_freq": "wifi_freq",
                    "wlan_hwmode": "wifi_hwmode",
                    "wlan_mode": "wifi_mode",
                    "wlan_txpower": "wifi_transmit_power",
                    "wlan_signal": "wifi_signal",
                    "wlan_noise": "wifi_noise",
                    "wlan_bitrate": "wifi_bitrate",
                    "wlan_vaps": "wifi_vaps_enabled",
                }.items():
            _update_value(wifi_attributes, key_to, data[key_from])
        wifi_attributes.save()
    elif interface.is_wifi():
        # alte wifi-Daten loeschen (anscheinend sind sie nicht mehr gueltig)
        WifiNetworkInterfaceAttributes.objects.filter(interface=interface).delete()


@transaction.atomic
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

