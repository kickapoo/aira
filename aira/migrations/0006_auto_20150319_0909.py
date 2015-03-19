# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0005_agrifield_custom_root_depth_max'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='custom_efficiency',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agrifield',
            name='custom_max_allow_depletion',
            field=models.DecimalField(null=True, max_digits=6, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agrifield',
            name='custom_root_depth_min',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
