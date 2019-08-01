# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0017_profile_email_language")]

    operations = [
        migrations.AlterField(
            model_name="agrifield",
            name="is_virtual",
            field=models.NullBooleanField(
                choices=[(True, "Yes"), (False, "No"), (None, "-")], default=None
            ),
        ),
        migrations.AlterField(
            model_name="agrifield",
            name="name",
            field=models.CharField(max_length=255, default="i.e. MyField1"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="email_language",
            field=models.CharField(
                max_length=3,
                choices=[("en", "English"), ("el", "Ελληνικά")],
                default="en",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="notification",
            field=models.CharField(
                max_length=3,
                blank=True,
                choices=[
                    ("D", "Day"),
                    ("2D", "2 Days"),
                    ("3D", "3 Days"),
                    ("4D", "4 Days"),
                    ("5D", "5 Days"),
                    ("7D", "Week"),
                    ("10D", "10 Day"),
                    ("30D", "Month"),
                ],
                default="",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="supervision_question",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")], default=False
            ),
        ),
    ]
