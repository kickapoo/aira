# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0018_agrifield_profile_additions'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdviceLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('inet', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agrifield', models.ForeignKey(to='aira.Agrifield')),
            ],
        ),
    ]
