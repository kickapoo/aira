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
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('area', models.FloatField()),
            ],
            options={
                'ordering': ('-name',),
                'verbose_name_plural': 'Agrifields',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CropType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ct_name', models.CharField(max_length=100)),
                ('ct_coeff', models.DecimalField(max_digits=6, decimal_places=2)),
                ('ct_rd', models.FloatField()),
            ],
            options={
                'ordering': ('-ct_name',),
                'verbose_name_plural': 'Crop Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IrrigationLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('water_amount', models.IntegerField()),
                ('agrifield', models.ForeignKey(to='aira.Agrifield')),
            ],
            options={
                'ordering': ('-time',),
                'get_latest_by': 'time',
                'verbose_name_plural': 'Irrigation Logs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IrrigationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('irrt_name', models.CharField(max_length=100)),
                ('irrt_eff', models.FloatField()),
            ],
            options={
                'ordering': ('-irrt_name',),
                'verbose_name_plural': 'Irrigation Types',
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
            model_name='agrifield',
            name='ct',
            field=models.ForeignKey(to='aira.CropType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agrifield',
            name='irrt',
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
