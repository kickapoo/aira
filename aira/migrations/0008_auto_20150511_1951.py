# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aira', '0007_profile_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='supervisor',
            field=models.ForeignKey(related_name=b'supervisor', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='notification',
            field=models.CharField(max_length=2, null=True, choices=[(b'D', 'Day'), (b'2D', '2 Days'), (b'3D', '3 Days'), (b'4D', '4 Days'), (b'5D', '5 Days'), (b'7D', 'Week'), (b'10D', '10 Day'), (b'30D', 'Month')]),
        ),
    ]
