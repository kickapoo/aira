# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0008_auto_20150511_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='supervision_question',
            field=models.BooleanField(default=False, choices=[(True, 'Yes'), (False, 'No')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='notification',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[('D', 'Day'), ('2D', '2 Days'), ('3D', '3 Days'), ('4D', '4 Days'), ('5D', '5 Days'), ('7D', 'Week'), ('10D', '10 Day'), ('30D', 'Month')]),
        ),
    ]
