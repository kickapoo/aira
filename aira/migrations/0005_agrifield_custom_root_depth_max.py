# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0004_auto_20150319_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='custom_root_depth_max',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
