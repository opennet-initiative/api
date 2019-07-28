import datetime
import re

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

from .utils import get_center_of_points, get_dynamic_site_radius


class AliveBaseManager(models.Manager):

    # nach dreißig Tagen gelten APs nicht mehr als "flapping", sondern als "offline"
    # Vorsicht: Werte synchron halten mit der "flapping"-Unterscheidung im der
    # on-map-Kartendarstellung.
    OFFLINE_AGE_MINUTES = 30 * 24 * 60
    FLAPPING_AGE_MINUTES = 30

    # Ein positiver "timedelta_minutes"-Wert führt zur Auslieferung von Objekten, deren
    # Zeitstempel älter als die angegebene Anzahl von Minuten ist. Ein negativer Wert liefert die
    # Objekte aus, deren Zeitstempel jünger ist (vergleichbar mit der "-mtime"-Konvention).
    timedelta_minutes = None

    def __init__(self, timestamp_fieldname):
        self.timestamp_fieldname = timestamp_fieldname
        super().__init__()

    def _filter_by_age(self, queryset, timedelta_minutes):
        """ bei Listen-Darstellugen filtern wir nach dem Alter der letzten Erreichbarkeit """
        limit_timestamp = datetime.datetime.now() - datetime.timedelta(
            minutes=abs(timedelta_minutes))
        if timedelta_minutes < 0:
            # liefere Objekte zurück, die sich vor weniger als "timedelta_minutes" gemeldet haben
            args = {"{}__gte".format(self.timestamp_fieldname): limit_timestamp}
            condition = Q(**args)
        else:
            # liefere Objekte zurück, die sich noch nie oder vor längerer Zeit gemeldet haben
            args = {"{}__lte".format(self.timestamp_fieldname): limit_timestamp}
            condition = Q(**args) | Q(**{"{}__isnull".format(self.timestamp_fieldname): True})
        return queryset.filter(condition)

    def get_queryset(self):
        return self.filter_by_status(super().get_queryset())


class OnlineManager(AliveBaseManager):
    def filter_by_status(self, queryset):
        return self._filter_by_age(queryset, -self.FLAPPING_AGE_MINUTES)


class OfflineManager(AliveBaseManager):
    def filter_by_status(self, queryset):
        return self._filter_by_age(queryset, self.OFFLINE_AGE_MINUTES)


class FlappingManager(AliveBaseManager):
    def filter_by_status(self, queryset):
        flapping_or_dead = self._filter_by_age(queryset, self.FLAPPING_AGE_MINUTES)
        return self._filter_by_age(flapping_or_dead, -self.OFFLINE_AGE_MINUTES)


class FirmwareVersionQuerySet(models.QuerySet):

    VERSION_REGEXES = {
        "airos": re.compile(r"^opennet0\.(\d)\.sdk$"),
        "openwrt-with-build-id": re.compile(
            r"^(?P<main>\d+(?:\.\d+)+)(?:-(?P<flag>unstable))?-(?P<sub>\d+)(?:-[a-f\d]+)?$"),
        "generic": re.compile(r"^(\d+(?:\.\d+)*)$"),
    }
    VERSION_FIELDNAME = "opennet_version"

    @classmethod
    def _get_comparable_tuple_for_version(cls, version_string):
        print(version_string)
        match = cls.VERSION_REGEXES["airos"].match(version_string)
        if match:
            return (-1, int(match.groups()[0]))
        match = cls.VERSION_REGEXES["openwrt-with-build-id"].match(version_string)
        if match:
            version_numbers = [int(value) for value in match.groupdict()["main"].split(".")]
            sub_version = int(match.groupdict()["sub"])
            flag_version = -1 if match.groupdict()["flag"] == "unstable" else 0
            return tuple(version_numbers + [flag_version, sub_version])
        match = cls.VERSION_REGEXES["generic"].match(version_string)
        if match:
            return tuple([int(value) for value in match.groups()[0].split(".")] + [0])
        return ()

    @classmethod
    def _get_all_versions(cls, queryset):
        return {item[cls.VERSION_FIELDNAME] for item in queryset.values(cls.VERSION_FIELDNAME)}

    def _filter_version_before_or_after(cls, queryset, reference_version: str, only_before: bool):
        reference_tuple = cls._get_comparable_tuple_for_version(reference_version)
        all_versions = cls._get_all_versions(queryset)
        older_versions = {
            version for version in all_versions
            if version and (reference_tuple > cls._get_comparable_tuple_for_version(version))}
        if only_before:
            valid_versions = older_versions
        else:
            # choose only versions after the reference_version
            valid_versions = all_versions.difference(older_versions.union(reference_version))
        return Q(**{"{}__in".format(cls.VERSION_FIELDNAME): valid_versions})

    def is_version(self, queryset, value):
        return queryset.filter(**{self.VERSION_FIELDNAME: value})

    def before_version(self, queryset, value):
        return queryset.filter(self._filter_version_before_or_after(queryset, value, True))

    def after_version(self, queryset, value):
        return queryset.filter(self._filter_version_before_or_after(queryset, value, False))


class AccessPointSite(models.Model):
    """ A location hosting multiple AccessPoints

    The Site content is mainly dynamically generated.  Thus it should be treated as a cache and not
    as a permanent storage for information.
    """

    @property
    def position(self):
        return get_center_of_points(ap.position for ap in self.accesspoints.all() if ap.position)

    @property
    def radius(self):
        return get_dynamic_site_radius(self.accesspoints.count())

    @property
    def post_address(self):
        addresses = [ap.post_address for ap in self.accesspoints.all() if ap.post_address]
        address_weights = sorted((addresses.count(address), address) for address in addresses)
        if address_weights:
            return address_weights[-1][1]
        else:
            return ""

    def __str__(self):
        site_details = []
        if self.post_address:
            site_details.append(self.post_address)
        site_details.append("{:d} APs".format(self.accesspoints.count()))
        return "Site #{:d} ({})".format(self.id, ", ".join(site_details))


class AccessPoint(models.Model):
    """Ein einzelner WLAN-Accesspoint im Opennet"""
    DISTRIBUTION_CHOICES = Choices("OpenWrt", "AirOS", "Lede", "LEDE")
    SERVICES_SORTING_CHOICES = Choices("manual", "hop", "etx")

    objects = GeoManager()
    online_objects = OnlineManager("lastseen_timestamp")
    offline_objects = OfflineManager("lastseen_timestamp")
    flapping_objects = FlappingManager("lastseen_timestamp")
    firmware_version_objects = FirmwareVersionQuerySet.as_manager()

    main_ip = models.GenericIPAddressField(primary_key=True)
    main_ipv6 = models.GenericIPAddressField(protocol="IPv6", null=True)
    post_address = models.TextField(null=True)
    antenna = models.TextField(null=True)
    position = gismodels.PointField(null=True, blank=True)
    owner = models.TextField(null=True)
    # Geraete-Modell (im Wiki eingetragen)
    device_model = models.TextField(null=True)
    lastseen_timestamp = models.DateTimeField(null=True)
    site = models.ForeignKey(AccessPointSite, related_name="accesspoints", null=True,
                             on_delete=models.SET_NULL)

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

    def __str__(self):
        return "AP %s owned by %s" % (self.main_ip, self.owner)


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

    def __str__(self):
        return ('EthernetNetworkInterface(ap="{}", name="{}", addresses=({}))'
                .format(self.accesspoint, self.if_name,
                        ", ".join(addr.address for addr in self.addresses.all())))


class NetworkInterfaceAddress(models.Model):

    ADRESS_FAMILIES = (("inet", "IPv4"), ("inet6", "IPv6"))

    # TODO: enthaelt das Django-Datenmodell bereits die Address-Family?
    address = models.GenericIPAddressField()
    family = StatusField(choices_name="ADRESS_FAMILIES")
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
    CRYPT_CHOICES = Choices("Plain", "WEP", "WPA-PSK", "WPA2-PSK")
    MODE_CHOICES = Choices("master", "client", "adhoc", "monitor")
    # die 802.11-Suffixe ("bgn" usw. werden beim Import alphabetisch sortiert)
    HWMODE_CHOICES = Choices("802.11bgn", "802.11an", "802.11bg", "802.11abg")
    WIFI_DRIVER_CHOICES = Choices("nl80211", "wl")

    interface = models.ForeignKey(EthernetNetworkInterface, primary_key=True,
                                  related_name="wifi_attributes", on_delete=models.CASCADE)
    wifi_ssid = models.CharField(max_length=32, null=True)
    wifi_bssid = models.CharField(max_length=17, null=True)
    wifi_driver = StatusField(choices_name="WIFI_DRIVER_CHOICES", null=True)
    wifi_hwmode = StatusField(choices_name="HWMODE_CHOICES", null=True)
    wifi_mode = StatusField(choices_name="MODE_CHOICES", null=True)
    wifi_channel = models.PositiveSmallIntegerField(null=True)
    wifi_freq = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    wifi_transmit_power = models.PositiveSmallIntegerField(null=True)
    wifi_signal = models.SmallIntegerField(null=True)
    wifi_noise = models.SmallIntegerField(null=True)
    wifi_bitrate = models.DecimalField(max_digits=6, decimal_places=1, null=True)
    wifi_crypt = StatusField(choices_name="CRYPT_CHOICES", null=True)
    wifi_vaps_enabled = models.NullBooleanField(default=False)

    def __str__(self):
        return ('WifiNetworkInterfaceAttributes(interface="{}", wifi_ssid="{}", wifi_mode="{}")'
                .format(self.interface, self.wifi_ssid, self.wifi_mode))


class RoutingLink(models.Model):
    """Eine Online-Verbindung zwischen Interfaces zweier APs

    ACHTUNG: derzeit sind die Routing-Link-Objekte defekt, da sie sich nicht auf die korrekten
    Interfaces beziehen, sondern immer auf diejenigen Interfaces der beteiligten APs, die mit der
    Main-IP des AP konfiguriert sind (siehe https://dev.opennet-initiative.de/ticket/212).
    """

    objects = models.Manager()
    online_objects = OnlineManager("timestamp")
    offline_objects = OfflineManager("timestamp")
    flapping_objects = FlappingManager("timestamp")

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
