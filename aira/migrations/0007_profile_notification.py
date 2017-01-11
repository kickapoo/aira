# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0006_auto_20150425_0055'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='notification',
            field=models.CharField(max_length=2, null=True, choices=[(b'D', 'Daily'), (b'2D', '2 Days'), (b'3D', '3 Days'), (b'4D', '4 Days'), (b'5D', '5 Days'), (b'7D', 'Weakly'), (b'10D', '10 Days'), (b'30D', 'Monthly')]),
            preserve_default=True,
        ),
    ]
