# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [("aira", "0012_auto_20150716_1748")]

    operations = [
        migrations.AlterField(
            model_name="agrifield",
            name="custom_irrigation_optimizer",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(1.0),
                    django.core.validators.MinValueValidator(0.1),
                ],
            ),
            preserve_default=True,
        )
    ]
