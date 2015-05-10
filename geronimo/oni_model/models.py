from django.db import models
from django.contrib.gis.db import models as gismodels
from model_utils.fields import StatusField
from model_utils import Choices


class AccessPoint(models.Model):
    """Ein einzelner WLAN-Accesspoint im Opennet"""
    DISTRIBUTION_CHOICES = Choices("OpenWrt", "AirOS")
    SERVICES_SORTING_CHOICES = Choices("manual", "hop", "etx")

    main_ip = models.IPAddressField(primary_key=True)
    post_address = models.TextField(null=True)
    antenna = models.TextField(null=True)
    position = gismodels.PointField(null=True, blank=True)
    objects = gismodels.GeoManager()
    owner = models.TextField(null=True)
    # Geraete-Modell (im Wiki eingetragen)
    device_model = models.TextField(null=True)
    timestamp = models.DateField(auto_now=True)

    # ondataservice-Daten
    device_board = models.TextField(null=True)
    device_architecture = models.TextField(null=True)
    device_cpu = models.TextField(null=True)
    device_memory_available = models.IntegerField(null=True)
    device_memory_free = models.IntegerField(null=True)

    system_kernel = models.TextField(null=True)
    system_watchdog_enabled = models.NullBooleanField()
    # TODO: ab Django 1.8 gibt es DurationField
    #system_uptime = models.DurationField(null=True)
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

    opennet_wifidog_enabled = models.NullBooleanField()
    opennet_wifidog_id = models.TextField(null=True)

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
        return RoutingLink.objects.filter(endpoints__interface__access_point=self)

    def __unicode__(self):
        return 'AP %s owned by %s' % (self.main_ip, self.owner)

    def __str__(self):
        return self.__unicode__()


class EthernetNetworkInterface(models.Model):
    """Eine der Kabelschnittstellen eines APs"""
    access_point = models.ForeignKey(AccessPoint, related_name="interfaces")

    if_name = models.CharField(max_length=128, null=True)
    if_is_bridge = models.BooleanField(default=False)
    if_is_bridged = models.BooleanField(default=False)
    if_hwaddress = models.TextField(null=True)
    ip_label = models.TextField(null=True)
    ip_address = models.IPAddressField()
    ip_broadcast = models.IPAddressField(null=True)
    opennet_networks = models.TextField(null=True)
    opennet_firewall_zones = models.TextField(null=True)
    olsr_enabled = models.BooleanField(default=False)

    # DHCP
    dhcp_range_start = models.IntegerField(null=True)
    dhcp_range_limit = models.IntegerField(null=True)
    dhcp_leasetime_seconds = models.IntegerField(null=True)
    dhcp_forward = models.BooleanField(default=False)

    # statistics
    ifstat_collisions = models.IntegerField(null=True)
    ifstat_rx_compressed = models.IntegerField(null=True)
    ifstat_rx_errors = models.IntegerField(null=True)
    ifstat_rx_length_errors = models.IntegerField(null=True)
    ifstat_rx_packets = models.IntegerField(null=True)
    ifstat_tx_carrier_errors = models.IntegerField(null=True)
    ifstat_tx_errors = models.IntegerField(null=True)
    ifstat_tx_packets = models.IntegerField(null=True)
    ifstat_multicast = models.IntegerField(null=True)
    ifstat_rx_crc_errors = models.IntegerField(null=True)
    ifstat_rx_fifo_errors = models.IntegerField(null=True)
    ifstat_rx_missed_errors = models.IntegerField(null=True)
    ifstat_tx_aborted_errors = models.IntegerField(null=True)
    ifstat_tx_compressed = models.IntegerField(null=True)
    ifstat_tx_fifo_errors = models.IntegerField(null=True)
    ifstat_tx_window_errors = models.IntegerField(null=True)
    ifstat_rx_bytes = models.IntegerField(null=True)
    ifstat_rx_dropped = models.IntegerField(null=True)
    ifstat_rx_frame_errors = models.IntegerField(null=True)
    ifstat_rx_over_errors = models.IntegerField(null=True)
    ifstat_tx_bytes = models.IntegerField(null=True)
    ifstat_tx_dropped = models.IntegerField(null=True)
    ifstat_tx_heartbeat_errors = models.IntegerField(null=True)

    def get_link_to(self, other):
        return RoutingLink.objects.filter(endpoints__interface=self).filter(endpoints__interface=other)[0]

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

    def __unicode__(self):
        return 'Interface %s of AP %s' % (self.ip_address, self.access_point.main_ip)

    def __str__(self):
        return self.__unicode__()


class WifiNetworkInterfaceAttributes(models.Model):
    """Eine der WLAN-Schnittstellen eines APs"""
    CRYPT_CHOICES = Choices('Plain', 'WEP','WPA2-PSK')
    MODE_CHOICES = Choices('master','client','adhoc')
    HWMODE_CHOICES = Choices('802.11bgn')
    WIFI_DRIVER_CHOICES = Choices('nl80211')

    interface = models.ForeignKey(EthernetNetworkInterface, primary_key=True)
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
    """Eine Online-Verbindung zwischen Interfaces zweier APs"""
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        ip_addrs = [iface_link.interface.ip_address for iface_link in self.endpoints.all()][:2]
        return "RoutingLink: %s <-> %s" % tuple(ip_addrs)


class InterfaceRoutingLink(models.Model):
    """Ein Ende eines gerichteten Links""" 
    interface = models.ForeignKey(EthernetNetworkInterface)
    routing_link = models.ForeignKey(RoutingLink, related_name="endpoints")
    quality = models.FloatField(default=0.0) #LQ von diesem Interface zum anderen

