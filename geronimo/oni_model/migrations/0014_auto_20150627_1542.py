# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0013_auto_20150627_1542'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accesspoint',
            old_name='timestamp',
            new_name='lastseen_timestamp',
        ),
    ]
