# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0006_auto_20150319_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='irrigation_optimizer',
            field=models.FloatField(default=1, choices=[(0.5, b'IRT(50% Inet)'), (0.75, b'IRT(75% Inet)'), (1, b'IRT(100% Inet)')]),
            preserve_default=True,
        ),
    ]
