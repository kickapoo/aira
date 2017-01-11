# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0017_profile_email_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrifield',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 19, 10, 36, 41, 303697, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
