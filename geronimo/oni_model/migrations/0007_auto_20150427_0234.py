# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0006_auto_20150427_0029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wifinetworkinterfaceattributes',
            name='id',
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='interface',
            field=models.ForeignKey(primary_key=True, serialize=False, to='oni_model.EthernetNetworkInterface'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_bitrate',
            field=models.DecimalField(decimal_places=1, max_digits=6, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_bssid',
            field=models.CharField(null=True, max_length=17),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_channel',
            field=models.PositiveSmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_crypt',
            field=model_utils.fields.StatusField(no_check_for_status=True, max_length=100, null=True, default='Plain', choices=[(0, 'dummy')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_driver',
            field=model_utils.fields.StatusField(no_check_for_status=True, max_length=100, null=True, default='nl80211', choices=[(0, 'dummy')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_freq',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_hwmode',
            field=model_utils.fields.StatusField(no_check_for_status=True, max_length=100, null=True, default='802.11bgn', choices=[(0, 'dummy')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_mode',
            field=model_utils.fields.StatusField(no_check_for_status=True, max_length=100, null=True, default='master', choices=[(0, 'dummy')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_noise',
            field=models.SmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_signal',
            field=models.SmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_ssid',
            field=models.CharField(null=True, max_length=32),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_transmit_power',
            field=models.PositiveSmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='wifi_vaps_enabled',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]
