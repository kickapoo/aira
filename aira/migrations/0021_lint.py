# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0020_kc_init_mid_end")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="email_language",
            field=models.CharField(
                default="en",
                max_length=3,
                choices=[("en", "English"), ("el", "Ελληνικά")],
            ),
        )
    ]
