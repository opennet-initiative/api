# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='node',
            name='long',
        ),
        migrations.AddField(
            model_name='node',
            name='position',
            field=django.contrib.gis.db.models.fields.PointField(default=None, srid=4326),
            preserve_default=True,
        ),
    ]
