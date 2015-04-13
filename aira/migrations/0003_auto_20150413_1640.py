# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0002_auto_20150411_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='custom_theta_s',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agrifield',
            name='custom_wilting_point',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
