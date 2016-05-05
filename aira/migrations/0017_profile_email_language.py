# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0016_auto_20160504_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_language',
            field=models.CharField(default=b'Gr', max_length=3, choices=[(b'Gr', b'English'), (b'El', b'\xce\x95\xce\xbb\xce\xbb\xce\xb7\xce\xbd\xce\xb9\xce\xba\xce\xac')]),
            preserve_default=True,
        ),
    ]
