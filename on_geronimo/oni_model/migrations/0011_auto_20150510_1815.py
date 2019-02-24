# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0010_auto_20150510_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ethernetnetworkinterface',
            name='access_point',
            field=models.ForeignKey(to='oni_model.AccessPoint', related_name='interfaces',
                                    on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
