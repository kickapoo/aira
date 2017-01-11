# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0019_advicelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='slug',
            field=models.SlugField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='agrifield',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
