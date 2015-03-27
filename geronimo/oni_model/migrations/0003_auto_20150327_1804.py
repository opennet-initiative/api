# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0002_auto_20150327_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessPoint',
            fields=[
                ('main_ip', models.IPAddressField(serialize=False, primary_key=True)),
                ('post_address', models.TextField()),
                ('antenna', models.TextField()),
                ('position', django.contrib.gis.db.models.fields.PointField(default=None, srid=4326)),
                ('owner', models.TextField()),
                ('device_model', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Node',
        ),
    ]
