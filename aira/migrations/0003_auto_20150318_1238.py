# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0002_agrifield_kc'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agrifield',
            old_name='kc',
            new_name='custom_kc',
        ),
        migrations.AddField(
            model_name='agrifield',
            name='use_custom_parameters',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
