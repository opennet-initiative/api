from django.db import models
from django.contrib.gis.db import models as gismodels


class AccessPoint(models.Model):
    main_ip = models.IPAddressField(primary_key=True)
    post_address = models.TextField()
    antenna = models.TextField()
    position = gismodels.PointField(null=True, blank=True)
    objects = gismodels.GeoManager()
    owner = models.TextField()
    device_model = models.TextField()

    sys_os_type = models.TextField()
    sys_os_name = models.TextField()

    def __unicode__(self):
        return '%s : %s' % (self.main_ip, self.owner)
    
    def __str__(self):
        return self.__unicode__()


class EthernetNetworkInterface(models.Model):
    access_point = models.ForeignKey(AccessPoint)

    if_name = models.TextField()
    if_is_bridge = models.BooleanField(default=False)
    if_is_bridged = models.BooleanField(default=False)
    if_hwaddress = models.TextField()
    ip_label = models.TextField()
    ip_address = models.IPAddressField()
    ip_broadcast = models.IPAddressField()
    opennet_networks = models.TextField()
    opennet_firewall_zones = models.TextField()
    olsr_enabled = models.BooleanField()

    # DHCP
    dhcp_range_start = models.IntegerField()
    dhcp_range_limit = models.IntegerField()
    dhcp_leasetime = models.IntegerField()
    dhcp_forward = models.BooleanField()

    # statistics
    ifstat_collisions = models.IntegerField()
    ifstat_rx_compressed = models.IntegerField()
    ifstat_rx_errors = models.IntegerField()
    ifstat_rx_length_errors = models.IntegerField()
    ifstat_rx_packets = models.IntegerField()
    ifstat_tx_carrier_errors = models.IntegerField()
    ifstat_tx_errors = models.IntegerField()
    ifstat_tx_packets = models.IntegerField()
    ifstat_multicast = models.IntegerField()
    ifstat_rx_crc_errors = models.IntegerField()
    ifstat_rx_fifo_errors = models.IntegerField()
    ifstat_rx_missed_errors = models.IntegerField()
    ifstat_tx_aborted_errors = models.IntegerField()
    ifstat_tx_compressed = models.IntegerField()
    ifstat_tx_fifo_errors = models.IntegerField()
    ifstat_tx_window_errors = models.IntegerField()
    ifstat_rx_bytes = models.IntegerField()
    ifstat_rx_dropped = models.IntegerField()
    ifstat_rx_frame_errors = models.IntegerField()
    ifstat_rx_over_errors = models.IntegerField()
    ifstat_tx_bytes = models.IntegerField()
    ifstat_tx_dropped = models.IntegerField()
    ifstat_tx_heart = models.IntegerField()


_CHOICES_WIFI_DRIVER = {"nl80211": "nl80211"}.items()
_CHOICES_WIFI_MODE = {"master": "master", "client": "client", "adhoc": "adhoc"}.items()
_CHOICES_WIFI_HWMODE = {"802.11bgn": "802.11bgn"}.items()
_CHOICES_WIFI_CRYPT = {"plain": "Plain", "wep": "WEP", "wpa2_psk": "WPA2-PSK"}.items()


class WifiNetworkInterface(EthernetNetworkInterface):
    wifi_ssid = models.TextField()
    wifi_bssid = models.TextField()
    wifi_driver = models.TextField(choices=_CHOICES_WIFI_DRIVER)
    wifi_hwmode = models.TextField(choices=_CHOICES_WIFI_HWMODE)
    wifi_mode = models.TextField(choices=_CHOICES_WIFI_MODE)
    wifi_channel = models.PositiveSmallIntegerField()
    wifi_freq = models.DecimalField(max_digits=6, decimal_places=3)
    wifi_txpower = models.PositiveSmallIntegerField()
    wifi_signal = models.SmallIntegerField()
    wifi_noise = models.SmallIntegerField()
    wifi_bitrate = models.DecimalField(max_digits=6, decimal_places=1)
    wifi_iw_crypt = models.TextField(choices=_CHOICES_WIFI_CRYPT)
    wifi_vaps_enabled = models.BooleanField()

