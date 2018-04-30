# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0018_agrifield_profile_additions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrifield',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
