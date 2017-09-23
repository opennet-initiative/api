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
                ('main_ip', models.IPAddressField(serialize=False, primary_key=True)),
                ('post_address', models.TextField()),
                ('antenna', models.TextField()),
                ('position', django.contrib.gis.db.models.fields.PointField(null=True, blank=True, srid=4326)),
                ('owner', models.TextField()),
                ('device_model', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
