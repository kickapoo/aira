# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0006_auto_20150425_0055'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='notification',
            field=models.CharField(max_length=2, null=True, choices=[('D', 'Daily'), ('2D', '2 Days'), ('3D', '3 Days'), ('4D', '4 Days'), ('5D', '5 Days'), ('7D', 'Weakly'), ('10D', '10 Days'), ('30D', 'Monthly')]),
            preserve_default=True,
        ),
    ]
