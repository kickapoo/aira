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
                ('name', models.CharField(default=b'i.e. Home Garden', max_length=255)),
                ('cadastre', models.IntegerField(null=True, blank=True)),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-name',),
                'verbose_name_plural': 'agrifields',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area', models.FloatField()),
                ('agrifield', models.ForeignKey(to='aira.Agrifield')),
            ],
            options={
                'ordering': ('-area',),
                'verbose_name_plural': 'crops',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CropType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('crop_coefficient', models.DecimalField(max_digits=6, decimal_places=2)),
                ('root_depth', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-name',),
                'verbose_name_plural': 'crop Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IrrigationLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('water_amount', models.IntegerField()),
                ('agrifield_crop', models.ForeignKey(to='aira.Crop')),
            ],
            options={
                'ordering': ('-time',),
                'get_latest_by': 'time',
                'verbose_name_plural': 'irrigation Logs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IrrigationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('efficiency', models.DecimalField(max_digits=2, decimal_places=2)),
            ],
            options={
                'ordering': ('-name',),
                'verbose_name_plural': 'irrigation Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(default=b'First Name', max_length=255)),
                ('last_name', models.CharField(default=b'Last Name', max_length=255)),
                ('address', models.CharField(default=b'Street/ZipCode/State', max_length=255, blank=True)),
                ('farmer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Profiles',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='crop',
            name='crop_type',
            field=models.ForeignKey(to='aira.CropType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crop',
            name='irrigation_type',
            field=models.ForeignKey(to='aira.IrrigationType'),
            preserve_default=True,
        ),
    ]
