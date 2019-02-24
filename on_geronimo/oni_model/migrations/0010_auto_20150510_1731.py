# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0009_auto_20150507_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interfaceroutinglink',
            name='quality',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interfaceroutinglink',
            name='routing_link',
            field=models.ForeignKey(related_name='endpoints', to='oni_model.RoutingLink',
                                    on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
