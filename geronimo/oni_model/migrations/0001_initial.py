# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessPoint',
            fields=[
                ('main_ip', models.IPAddressField(primary_key=True, serialize=False)),
                ('post_address', models.TextField()),
                ('antenna', models.TextField()),
                ('position', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, default=None, srid=4326)),
                ('owner', models.TextField()),
                ('device_model', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
