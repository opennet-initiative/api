# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0003_auto_20150328_0001'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wifinetworkinterface',
            old_name='wifi_txpower',
            new_name='wifi_transmit_power',
        ),
        migrations.RemoveField(
            model_name='ethernetnetworkinterface',
            name='dhcp_leasetime',
        ),
        migrations.AddField(
            model_name='ethernetnetworkinterface',
            name='dhcp_leasetime_seconds',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='dhcp_range_limit',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='dhcp_range_start',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
