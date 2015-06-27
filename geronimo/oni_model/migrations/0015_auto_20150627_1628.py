# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0014_auto_20150627_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='lastseen_timestamp',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
