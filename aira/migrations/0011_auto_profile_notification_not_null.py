# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0010_auto_20150531_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='notification',
            field=models.CharField(default='', max_length=2, blank=True, choices=[('D', 'Day'), ('2D', '2 Days'), ('3D', '3 Days'), ('4D', '4 Days'), ('5D', '5 Days'), ('7D', 'Week'), ('10D', '10 Day'), ('30D', 'Month')]),
            preserve_default=True,
        ),
    ]
