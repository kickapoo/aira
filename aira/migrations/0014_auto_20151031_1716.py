# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0013_auto_20150716_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='notification',
            field=models.CharField(default=b'', max_length=3, blank=True, choices=[(b'D', 'Day'), (b'2D', '2 Days'), (b'3D', '3 Days'), (b'4D', '4 Days'), (b'5D', '5 Days'), (b'7D', 'Week'), (b'10D', '10 Day'), (b'30D', 'Month')]),
            preserve_default=True,
        ),
    ]
