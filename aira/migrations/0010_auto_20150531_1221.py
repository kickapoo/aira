# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0009_auto_20150516_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='irrigationlog',
            name='applied_water',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
