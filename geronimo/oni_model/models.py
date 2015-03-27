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


class EthernetNetworkInterface(models.Model):
    access_point = models.ForeignKey(AccessPoint)

    if_name = models.TextField()
    if_type_bridge = models.TextField()
    if_type_bridgedif = models.TextField()
    if_hwaddress = models.TextField()
    ip_label = models.TextField()
    ip_address = models.IPAddressField()
    ip_broadcast = models.IPAddressField()
    on_networks = models.TextField()
    on_zones = models.TextField()
    on_olsr = models.BooleanField()

    # DHCP
    dhcp_start = models.IntegerField()
    dhcp_limit = models.IntegerField()
    dhcp_leasetime = models.IntegerField()
    dhcp_fwd = models.BooleanField()

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
    ssid = models.TextField()
    bssid = models.TextField()
    driver = models.TextField(choices=_CHOICES_WIFI_DRIVER)
    hwmode = models.TextField(choices=_CHOICES_WIFI_HWMODE)
    mode = models.TextField(choices=_CHOICES_WIFI_MODE)
    channel = models.PositiveSmallIntegerField()
    freq = models.DecimalField(max_digits=6, decimal_places=3)
    txpower = models.PositiveSmallIntegerField()
    signal = models.SmallIntegerField()
    noise = models.SmallIntegerField()
    bitrate = models.DecimalField(max_digits=6, decimal_places=1)
    crypt = models.TextField(choices=_CHOICES_WIFI_CRYPT)
    vaps_enabled = models.BooleanField()

    def __unicode__(self):
        return '%s : %s' % (self.main_ip, self.owner)
    
    def __str__(self):
        return self.__unicode__()

