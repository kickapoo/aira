# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0021_auto_20170130_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrifield',
            name='crop_type',
            field=models.ForeignKey(blank=True, to='aira.CropType', null=True),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='irrigation_type',
            field=models.ForeignKey(blank=True, to='aira.IrrigationType', null=True),
        ),
    ]
