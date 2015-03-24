# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0007_agrifield_irrigation_optimizer'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='custom_irrigation_optimizer',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='area',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='irrigation_optimizer',
            field=models.FloatField(default=1.0, choices=[(0.5, b'IRT (50% Inet)'), (0.75, b'IRT (75% Inet)'), (1.0, b'IRT (100% Inet)')]),
        ),
    ]
