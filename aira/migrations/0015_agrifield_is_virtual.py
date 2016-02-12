# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0014_auto_20151031_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='is_virtual',
            field=models.NullBooleanField(default=None, choices=[(True, 'Yes'), (False, 'No'), (None, b'-')]),
            preserve_default=True,
        ),
    ]
