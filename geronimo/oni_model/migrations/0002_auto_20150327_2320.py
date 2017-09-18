# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EthernetNetworkInterface',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('if_name', models.CharField(max_length=128)),
                ('if_is_bridge', models.BooleanField(default=False)),
                ('if_is_bridged', models.BooleanField(default=False)),
                ('if_hwaddress', models.TextField()),
                ('ip_label', models.TextField()),
                ('ip_address', models.IPAddressField()),
                ('ip_broadcast', models.IPAddressField()),
                ('opennet_networks', models.TextField()),
                ('opennet_firewall_zones', models.TextField()),
                ('olsr_enabled', models.BooleanField(default=False)),
                ('dhcp_range_start', models.IntegerField()),
                ('dhcp_range_limit', models.IntegerField()),
                ('dhcp_leasetime', models.IntegerField()),
                ('dhcp_forward', models.BooleanField(default=False)),
                ('ifstat_collisions', models.IntegerField()),
                ('ifstat_rx_compressed', models.IntegerField()),
                ('ifstat_rx_errors', models.IntegerField()),
                ('ifstat_rx_length_errors', models.IntegerField()),
                ('ifstat_rx_packets', models.IntegerField()),
                ('ifstat_tx_carrier_errors', models.IntegerField()),
                ('ifstat_tx_errors', models.IntegerField()),
                ('ifstat_tx_packets', models.IntegerField()),
                ('ifstat_multicast', models.IntegerField()),
                ('ifstat_rx_crc_errors', models.IntegerField()),
                ('ifstat_rx_fifo_errors', models.IntegerField()),
                ('ifstat_rx_missed_errors', models.IntegerField()),
                ('ifstat_tx_aborted_errors', models.IntegerField()),
                ('ifstat_tx_compressed', models.IntegerField()),
                ('ifstat_tx_fifo_errors', models.IntegerField()),
                ('ifstat_tx_window_errors', models.IntegerField()),
                ('ifstat_rx_bytes', models.IntegerField()),
                ('ifstat_rx_dropped', models.IntegerField()),
                ('ifstat_rx_frame_errors', models.IntegerField()),
                ('ifstat_rx_over_errors', models.IntegerField()),
                ('ifstat_tx_bytes', models.IntegerField()),
                ('ifstat_tx_dropped', models.IntegerField()),
                ('ifstat_tx_heart', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WifiNetworkInterface',
            fields=[
                ('ethernetnetworkinterface_ptr', models.OneToOneField(to='oni_model.EthernetNetworkInterface', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('wifi_ssid', models.CharField(max_length=32)),
                ('wifi_bssid', models.CharField(max_length=17)),
                ('wifi_driver', model_utils.fields.StatusField(no_check_for_status=True, default='nl80211', max_length=100, choices=[('nl80211', 'nl80211')])),
                ('wifi_hwmode', model_utils.fields.StatusField(no_check_for_status=True, default='802.11bgn', max_length=100, choices=[('802.11bgn', '802.11bgn')])),
                ('wifi_mode', model_utils.fields.StatusField(no_check_for_status=True, default='master', max_length=100, choices=[('master', 'master'), ('client', 'client'), ('adhoc', 'adhoc')])),
                ('wifi_channel', models.PositiveSmallIntegerField()),
                ('wifi_freq', models.DecimalField(max_digits=6, decimal_places=3)),
                ('wifi_txpower', models.PositiveSmallIntegerField()),
                ('wifi_signal', models.SmallIntegerField()),
                ('wifi_noise', models.SmallIntegerField()),
                ('wifi_bitrate', models.DecimalField(max_digits=6, decimal_places=1)),
                ('wifi_crypt', model_utils.fields.StatusField(no_check_for_status=True, default='Plain', max_length=100, choices=[('Plain', 'Plain'), ('WEP', 'WEP'), ('WPA2-PSK', 'WPA2-PSK')])),
                ('wifi_vaps_enabled', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=('oni_model.ethernetnetworkinterface',),
        ),
        migrations.AddField(
            model_name='ethernetnetworkinterface',
            name='access_point',
            field=models.ForeignKey(to='oni_model.AccessPoint'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='sys_os_name',
            field=models.TextField(null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='sys_os_type',
            field=models.TextField(null=True, default=None),
            preserve_default=True,
        ),
    ]
