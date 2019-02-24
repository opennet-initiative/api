# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import model_utils.fields
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0005_auto_20150328_0353'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterfaceRoutingLink',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('quality', models.FloatField()),
                ('interface', models.ForeignKey(to='oni_model.EthernetNetworkInterface',
                                                on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoutingLink',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WifiNetworkInterfaceAttributes',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('wifi_ssid', models.CharField(max_length=32)),
                ('wifi_bssid', models.CharField(max_length=17)),
                ('wifi_driver', model_utils.fields.StatusField(no_check_for_status=True, choices=[('nl80211', 'nl80211')], default='nl80211', max_length=100)),
                ('wifi_hwmode', model_utils.fields.StatusField(no_check_for_status=True, choices=[('802.11bgn', '802.11bgn')], default='802.11bgn', max_length=100)),
                ('wifi_mode', model_utils.fields.StatusField(no_check_for_status=True, choices=[('master', 'master'), ('client', 'client'), ('adhoc', 'adhoc')], default='master', max_length=100)),
                ('wifi_channel', models.PositiveSmallIntegerField()),
                ('wifi_freq', models.DecimalField(max_digits=6, decimal_places=3)),
                ('wifi_transmit_power', models.PositiveSmallIntegerField()),
                ('wifi_signal', models.SmallIntegerField()),
                ('wifi_noise', models.SmallIntegerField()),
                ('wifi_bitrate', models.DecimalField(max_digits=6, decimal_places=1)),
                ('wifi_crypt', model_utils.fields.StatusField(no_check_for_status=True, choices=[('Plain', 'Plain'), ('WEP', 'WEP'), ('WPA2-PSK', 'WPA2-PSK')], default='Plain', max_length=100)),
                ('wifi_vaps_enabled', models.BooleanField(default=False)),
                ('interface', models.ForeignKey(to='oni_model.EthernetNetworkInterface',
                                                on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='wifinetworkinterface',
            name='ethernetnetworkinterface_ptr',
        ),
        migrations.DeleteModel(
            name='WifiNetworkInterface',
        ),
        migrations.AddField(
            model_name='interfaceroutinglink',
            name='routing_link',
            field=models.ForeignKey(to='oni_model.RoutingLink', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='timestamp',
            field=models.DateField(default=datetime.datetime(2015, 4, 27, 0, 29, 39, 760918, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='if_hwaddress',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='if_name',
            field=models.CharField(null=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_collisions',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_multicast',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_bytes',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_compressed',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_crc_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_dropped',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_fifo_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_frame_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_length_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_missed_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_over_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_rx_packets',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_aborted_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_bytes',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_carrier_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_compressed',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_dropped',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_fifo_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_heartbeat_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_packets',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ifstat_tx_window_errors',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ip_broadcast',
            field=models.IPAddressField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ip_label',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='opennet_firewall_zones',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='opennet_networks',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
