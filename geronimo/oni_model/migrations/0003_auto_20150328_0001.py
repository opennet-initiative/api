# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0002_auto_20150327_2320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ethernetnetworkinterface',
            old_name='ifstat_tx_heart',
            new_name='ifstat_tx_heartbeat_errors',
        ),
    ]
