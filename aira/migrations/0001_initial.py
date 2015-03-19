# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agrifield',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'i.e. MyField1', max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('area', models.FloatField()),
            ],
            options={
                'ordering': ('name', 'area'),
                'verbose_name_plural': 'Agrifields',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CropType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('root_depth_max', models.FloatField()),
                ('root_depth_min', models.FloatField()),
                ('max_allow_depletion', models.DecimalField(max_digits=6, decimal_places=2)),
                ('kc', models.FloatField()),
                ('fek_category', models.IntegerField()),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Crop Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IrrigationLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('applied_water', models.IntegerField()),
                ('agrifield', models.ForeignKey(to='aira.Agrifield')),
            ],
            options={
                'ordering': ('time',),
                'get_latest_by': 'time',
                'verbose_name_plural': 'Irrigation Logs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IrrigationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('efficiency', models.FloatField()),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Irrigation Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255, blank=True)),
                ('farmer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Profiles',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='agrifield',
            name='crop_type',
            field=models.ForeignKey(to='aira.CropType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agrifield',
            name='irrigation_type',
            field=models.ForeignKey(to='aira.IrrigationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agrifield',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
