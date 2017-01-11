# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0020_auto_20161229_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrifield',
            name='area',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
