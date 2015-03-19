# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0003_auto_20150318_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrifield',
            name='custom_kc',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
