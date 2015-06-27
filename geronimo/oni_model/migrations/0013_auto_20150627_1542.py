# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0012_auto_20150510_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
    ]
