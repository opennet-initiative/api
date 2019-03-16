from django.db import models
from django.db.models.query_utils import Q
from django.contrib.gis.db import models as gismodels
try:
    from django.contrib.gis.db.models.manager import GeoManager
except ImportError:
    # GeoManager was removed in Django 2.0. The usual manager should be sufficient now.
    GeoManager = models.Manager
import django.contrib.gis.geos.linestring
from model_utils.fields import StatusField
from model_utils import Choices


class AccessPoint(models.Model):
    """Ein einzelner WLAN-Accesspoint im Opennet"""
    DISTRIBUTION_CHOICES = Choices("OpenWrt", "AirOS", "Lede", "LEDE")
    SERVICES_SORTING_CHOICES = Choices("manual", "hop", "etx")

    main_ip = models.GenericIPAddressField(primary_key=True)
    post_address = models.TextField(null=True)
    antenna = models.TextField(null=True)
    position = gismodels.PointField(null=True, blank=True)
    objects = GeoManager()
    owner = models.TextField(null=True)
    # Geraete-Modell (im Wiki eingetragen)
    device_model = models.TextField(null=True)
    lastseen_timestamp = models.DateTimeField(null=True)

    # ondataservice-Daten
    device_board = models.TextField(null=True)
    device_architecture = models.TextField(null=True)
    device_cpu = models.TextField(null=True)
    device_memory_available = models.IntegerField(null=True)
    device_memory_free = models.IntegerField(null=True)

    system_kernel = models.TextField(null=True)
    system_watchdog_enabled = models.NullBooleanField()
    # TODO: ab Django 1.8 gibt es DurationField
#   system_uptime = models.DurationField(null=True)
    system_uptime = models.IntegerField(null=True)
    system_load_1min = models.FloatField(null=True)
    system_load_5min = models.FloatField(null=True)
    system_load_15min = models.FloatField(null=True)

    firmware_type = StatusField(null=True, choices_name="DISTRIBUTION_CHOICES")
    firmware_release_name = models.TextField(null=True)
    firmware_release_version = models.TextField(null=True)
    firmware_build = models.TextField(null=True)
    firmware_install_timestamp = models.DateField(null=True)

    opennet_version = models.TextField(null=True)
    opennet_install_timestamp = models.DateField(null=True)
    opennet_packages = models.TextField(null=True)
    opennet_id = models.TextField(null=True)
    olsrd_running = models.NullBooleanField()
    olsrd_main_ip = models.TextField(null=True)

    opennet_captive_portal_enabled = models.NullBooleanField()
    opennet_captive_portal_name = models.TextField(null=True)

    opennet_certificate_cn = models.TextField(null=True)
    opennet_vpn_internet_enabled = models.NullBooleanField()
    opennet_vpn_internet_connections = models.TextField(null=True)
    opennet_vpn_internet_autosearch = models.TextField(null=True)
    opennet_services_sorting = StatusField(null=True, choices_name="SERVICES_SORTING_CHOICES")
    opennet_vpn_internet_gateways = models.TextField(null=True)
    opennet_vpn_internet_blacklist = models.TextField(null=True)

    opennet_service_relay_connected = models.NullBooleanField()
    opennet_service_relay_enabled = models.NullBooleanField()

    opennet_vpn_mesh_connected = models.NullBooleanField()
    opennet_vpn_mesh_connections = models.TextField(null=True)
    opennet_vpn_mesh_gateways = models.TextField(null=True)
    opennet_vpn_mesh_gateway_names = models.TextField(null=True)

    def get_links(self):
        return RoutingLink.objects.filter(endpoints__interface__accesspoint=self)

    def __unicode__(self):
        return 'AP %s owned by %s' % (self.main_ip, self.owner)

    def __str__(self):
        return self.__unicode__()


class EthernetNetworkInterface(models.Model):
    """Eine der Kabelschnittstellen eines APs"""
    accesspoint = models.ForeignKey(AccessPoint, related_name="interfaces",
                                    on_delete=models.CASCADE)

    if_name = models.CharField(max_length=128, null=True)
    if_is_bridge = models.BooleanField(default=False)
    if_is_bridged = models.BooleanField(default=False)
    if_hwaddress = models.TextField(null=True)
    opennet_networks = models.TextField(null=True)
    opennet_firewall_zones = models.TextField(null=True)
    olsr_enabled = models.BooleanField(default=False)

    # DHCP
    dhcp_range_start = models.IntegerField(null=True)
    dhcp_range_limit = models.IntegerField(null=True)
    dhcp_leasetime_seconds = models.IntegerField(null=True)
    dhcp_forward = models.BooleanField(default=False)

    # statistics
    ifstat_collisions = models.BigIntegerField(null=True)
    ifstat_rx_compressed = models.BigIntegerField(null=True)
    ifstat_rx_errors = models.BigIntegerField(null=True)
    ifstat_rx_length_errors = models.BigIntegerField(null=True)
    ifstat_rx_packets = models.BigIntegerField(null=True)
    ifstat_tx_carrier_errors = models.BigIntegerField(null=True)
    ifstat_tx_errors = models.BigIntegerField(null=True)
    ifstat_tx_packets = models.BigIntegerField(null=True)
    ifstat_multicast = models.BigIntegerField(null=True)
    ifstat_rx_crc_errors = models.BigIntegerField(null=True)
    ifstat_rx_fifo_errors = models.BigIntegerField(null=True)
    ifstat_rx_missed_errors = models.BigIntegerField(null=True)
    ifstat_tx_aborted_errors = models.BigIntegerField(null=True)
    ifstat_tx_compressed = models.BigIntegerField(null=True)
    ifstat_tx_fifo_errors = models.BigIntegerField(null=True)
    ifstat_tx_window_errors = models.BigIntegerField(null=True)
    ifstat_rx_bytes = models.BigIntegerField(null=True)
    ifstat_rx_dropped = models.BigIntegerField(null=True)
    ifstat_rx_frame_errors = models.BigIntegerField(null=True)
    ifstat_rx_over_errors = models.BigIntegerField(null=True)
    ifstat_tx_bytes = models.BigIntegerField(null=True)
    ifstat_tx_dropped = models.BigIntegerField(null=True)
    ifstat_tx_heartbeat_errors = models.BigIntegerField(null=True)

    def get_link_to(self, other):
        return RoutingLink.objects.filter(
            endpoints__interface=self).filter(endpoints__interface=other)[0]

    def get_or_create_link_to(self, other):
        try:
            linker = self.get_link_to(other)
            return linker, False
        except IndexError:
            pass
        # erstelle neues Objekt und seine Verbindungen zu den beiden Interfaces
        linker = RoutingLink.objects.create()
        for iface in (self, other):
            link_info = InterfaceRoutingLink.objects.create(routing_link=linker, interface=iface)
            link_info.save()
        return linker, True

    def is_wireless(self):
        # check for known wireless attributes
        if self.wifi_attributes.exists():
            return True
        # compare the interface name
        if self.if_name:
            lower_name = self.if_name.lower()
            for wifi_prefix in ("wlan", "ath"):
                if lower_name.startswith(wifi_prefix):
                    return True
        return False

    @classmethod
    def get_filter_for_ipaddress(cls, address_obj):
        family = NetworkInterfaceAddress.get_address_family_from_ipaddress(address_obj)
        return Q(addresses__address=str(address_obj.ip),
                 addresses__family=family,
                 addresses__netmask_prefixlen=address_obj.network.prefixlen)

    def __unicode__(self):
        return 'Interface %s of AP %s' % ((addr.address for addr in self.addresses.all()),
                                          self.accesspoint.main_ip)

    def __str__(self):
        return self.__unicode__()


class NetworkInterfaceAddress(models.Model):

    ADRESS_FAMILIES = (("inet", "IPv4"), ("inet6", "IPv6"))

    # TODO: enthaelt das Django-Datenmodell bereits die Address-Family?
    address = models.GenericIPAddressField()
    family = StatusField(choices_name='ADRESS_FAMILIES')
    interface = models.ForeignKey(EthernetNetworkInterface, related_name="addresses",
                                  on_delete=models.CASCADE)
    netmask_prefixlen = models.IntegerField()

    @classmethod
    def get_address_family_from_ipaddress(cls, address_obj):
        return {4: "inet", 6: "inet6"}[address_obj.version]

    @classmethod
    def create_with_ipaddress(cls, interface, address_obj):
        family = cls.get_address_family_from_ipaddress(address_obj)
        return cls.objects.create(interface=interface, address=str(address_obj.ip), family=family,
                                  netmask_prefixlen=address_obj.network.prefixlen)

    @classmethod
    def get_filter_for_ipaddress(cls, address_obj):
        family = cls.get_address_family_from_ipaddress(address_obj)
        return Q(address=str(address_obj.ip),
                 family=family,
                 netmask_prefixlen=address_obj.network.prefixlen)


class WifiNetworkInterfaceAttributes(models.Model):
    """Eine der WLAN-Schnittstellen eines APs"""
    CRYPT_CHOICES = Choices('Plain', 'WEP', 'WPA-PSK', 'WPA2-PSK')
    MODE_CHOICES = Choices('master', 'client', 'adhoc', 'monitor')
    # die 802.11-Suffixe ("bgn" usw. werden beim Import alphabetisch sortiert)
    HWMODE_CHOICES = Choices('802.11bgn', '802.11an', '802.11bg', '802.11abg')
    WIFI_DRIVER_CHOICES = Choices('nl80211', 'wl')

    interface = models.ForeignKey(EthernetNetworkInterface, primary_key=True,
                                  related_name="wifi_attributes", on_delete=models.CASCADE)
    wifi_ssid = models.CharField(max_length=32, null=True)
    wifi_bssid = models.CharField(max_length=17, null=True)
    wifi_driver = StatusField(choices_name='WIFI_DRIVER_CHOICES', null=True)
    wifi_hwmode = StatusField(choices_name='HWMODE_CHOICES', null=True)
    wifi_mode = StatusField(choices_name='MODE_CHOICES', null=True)
    wifi_channel = models.PositiveSmallIntegerField(null=True)
    wifi_freq = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    wifi_transmit_power = models.PositiveSmallIntegerField(null=True)
    wifi_signal = models.SmallIntegerField(null=True)
    wifi_noise = models.SmallIntegerField(null=True)
    wifi_bitrate = models.DecimalField(max_digits=6, decimal_places=1, null=True)
    wifi_crypt = StatusField(choices_name='CRYPT_CHOICES', null=True)
    wifi_vaps_enabled = models.NullBooleanField(default=False)


class RoutingLink(models.Model):
    """Eine Online-Verbindung zwischen Interfaces zweier APs

    ACHTUNG: derzeit sind die Routing-Link-Objekte defekt, da sie sich nicht auf die korrekten
    Interfaces beziehen, sondern immer auf diejenigen Interfaces der beteiligten APs, die mit der
    Main-IP des AP konfiguriert sind (siehe https://dev.opennet-initiative.de/ticket/212).
    """

    timestamp = models.DateTimeField(auto_now=True)

    @property
    def wifi_ssid(self):
        for iface_link in self.endpoints.all():
            for wifi_settings in iface_link.interface.wifi_attributes.all():
                if wifi_settings.wifi_ssid:
                    return wifi_settings.wifi_ssid
        else:
            return None

    @property
    def quality(self):
        result = 1.0
        for value in (iface_link.quality for iface_link in self.endpoints.all()):
            result *= value
        return result

    @property
    def position(self):
        positions = []
        for iface_link in self.endpoints.all():
            node = iface_link.interface.accesspoint
            if node.position:
                positions.append(node.position)
        if len(positions) > 1:
            return django.contrib.gis.geos.linestring.LineString(positions)
        else:
            return None

    @property
    def is_wireless(self):
        for iface_link in self.endpoints.all():
            if iface_link.interface.is_wireless():
                return True
        return False

    def __str__(self):
        ip_addrs = [iface_link.interface.addresses.first()
                    for iface_link in self.endpoints.all()][:2]
        return "RoutingLink: {}".format(ip_addrs)


class InterfaceRoutingLink(models.Model):
    """Ein Ende eines gerichteten Links"""
    interface = models.ForeignKey(EthernetNetworkInterface, on_delete=models.CASCADE)
    routing_link = models.ForeignKey(RoutingLink, related_name="endpoints",
                                     on_delete=models.CASCADE)
    # Link quality von diesem Interface zum anderen
    quality = models.FloatField(default=0.0)
