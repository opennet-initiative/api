# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-20 00:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0013_auto_20150627_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='main_ip',
            field=models.GenericIPAddressField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ip_address',
            field=models.GenericIPAddressField(),
        ),
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='ip_broadcast',
            field=models.GenericIPAddressField(null=True),
        ),
    ]
