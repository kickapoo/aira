# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0011_auto_profile_notification_not_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrifield',
            name='irrigation_optimizer',
            field=models.FloatField(default=0.5),
            preserve_default=True,
        ),
    ]
