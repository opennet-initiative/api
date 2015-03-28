from django.db import models
from django.contrib.gis.db import models as gismodels
from model_utils.fields import StatusField
from model_utils import Choices

class AccessPoint(models.Model):
    main_ip = models.IPAddressField(primary_key=True)
    post_address = models.TextField()
    antenna = models.TextField()
    position = gismodels.PointField(null=True, blank=True)
    objects = gismodels.GeoManager()
    owner = models.TextField()
    device_model = models.TextField()

    sys_os_type = models.TextField(null=True,default=None)
    sys_os_name = models.TextField(null=True,default=None)

    def __unicode__(self):
        return '%s : %s' % (self.main_ip, self.owner)
    
    def __str__(self):
        return self.__unicode__()


class EthernetNetworkInterface(models.Model):
    access_point = models.ForeignKey(AccessPoint)

    if_name = models.CharField(max_length=128)
    if_is_bridge = models.BooleanField(default=False)
    if_is_bridged = models.BooleanField(default=False)
    if_hwaddress = models.TextField()
    ip_label = models.TextField()
    ip_address = models.IPAddressField()
    ip_broadcast = models.IPAddressField()
    opennet_networks = models.TextField()
    opennet_firewall_zones = models.TextField()
    olsr_enabled = models.BooleanField(default=False)

    # DHCP
    dhcp_range_start = models.IntegerField(null=True)
    dhcp_range_limit = models.IntegerField(null=True)
    dhcp_leasetime_seconds = models.IntegerField(null=True)
    dhcp_forward = models.BooleanField(default=False)

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
    ifstat_tx_heartbeat_errors = models.IntegerField()


class WifiNetworkInterface(EthernetNetworkInterface):
    CRYPT_CHOICES = Choices('Plain', 'WEP','WPA2-PSK')
    MODE_CHOICES = Choices('master','client','adhoc')
    HWMODE_CHOICES = Choices('802.11bgn')
    WIFI_DRIVER_CHOICES = Choices('nl80211')

    wifi_ssid = models.CharField(max_length=32)
    wifi_bssid = models.CharField(max_length=17)
    wifi_driver = StatusField(choices_name='WIFI_DRIVER_CHOICES')
    wifi_hwmode = StatusField(choices_name='HWMODE_CHOICES')
    wifi_mode = StatusField(choices_name='MODE_CHOICES')
    wifi_channel = models.PositiveSmallIntegerField()
    wifi_freq = models.DecimalField(max_digits=6, decimal_places=3)
    wifi_transmit_power = models.PositiveSmallIntegerField()
    wifi_signal = models.SmallIntegerField()
    wifi_noise = models.SmallIntegerField()
    wifi_bitrate = models.DecimalField(max_digits=6, decimal_places=1)
    wifi_crypt = StatusField(choices_name='CRYPT_CHOICES')
    wifi_vaps_enabled = models.BooleanField(default=False)

