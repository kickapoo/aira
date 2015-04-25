# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0005_auto_20150419_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='farmer',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
