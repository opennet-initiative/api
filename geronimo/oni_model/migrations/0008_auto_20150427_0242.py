# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oni_model', '0007_auto_20150427_0234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='opennet_services_sorting',
            field=model_utils.fields.StatusField(null=True, choices=[(0, 'dummy')], default='manual', no_check_for_status=True, max_length=100),
            preserve_default=True,
        ),
    ]
