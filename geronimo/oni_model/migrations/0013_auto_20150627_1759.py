# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0012_auto_20150510_1953'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accesspoint',
            old_name='opennet_wifidog_enabled',
            new_name='opennet_captive_portal_enabled',
        ),
        migrations.RenameField(
            model_name='accesspoint',
            old_name='opennet_wifidog_id',
            new_name='opennet_captive_portal_name',
        ),
        migrations.RemoveField(
            model_name='accesspoint',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='lastseen_timestamp',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
