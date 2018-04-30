# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0019_auto_20180430_1316'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdviceLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inet', models.CharField(max_length=10)),
                ('advice', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agrifield', models.ForeignKey(to='aira.Agrifield')),
            ],
        ),
    ]
