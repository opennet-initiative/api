# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('ip', models.IPAddressField(primary_key=True, serialize=False)),
                ('post_address', models.TextField()),
                ('antenna', models.TextField()),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
                ('owner', models.TextField()),
                ('device', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
