# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0004_auto_20150413_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrifield',
            name='custom_efficiency',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1.0), django.core.validators.MinValueValidator(0.05)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_field_capacity',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(0.45), django.core.validators.MinValueValidator(0.1)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_irrigation_optimizer',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2.0), django.core.validators.MinValueValidator(0.5)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_kc',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1.5), django.core.validators.MinValueValidator(0.1)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_max_allow_depletion',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(1.0), django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_root_depth_max',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(4.0), django.core.validators.MinValueValidator(0.2)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_root_depth_min',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2.0), django.core.validators.MinValueValidator(0.1)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_thetaS',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(0.55), django.core.validators.MinValueValidator(0.3)]),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='custom_wilting_point',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(0.22), django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='irrigationlog',
            name='applied_water',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
