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
                default=b"en",
                max_length=3,
                choices=[
                    (b"en", b"English"),
                    (
                        b"el",
                        b"\xce\x95\xce\xbb\xce\xbb\xce\xb7\xce"
                        b"\xbd\xce\xb9\xce\xba\xce\xac",
                    ),
                ],
            ),
        )
    ]
