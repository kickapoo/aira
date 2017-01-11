# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0018_agrifield_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdviceLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inet', models.CharField(max_length=10)),
                ('advice', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agrifield', models.ForeignKey(to='aira.Agrifield')),
            ],
        ),
    ]
