# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0011_auto_20150510_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wifinetworkinterfaceattributes',
            name='interface',
            field=models.ForeignKey(related_name='wifi_attributes', serialize=False, primary_key=True, to='oni_model.EthernetNetworkInterface'),
            preserve_default=True,
        ),
    ]
