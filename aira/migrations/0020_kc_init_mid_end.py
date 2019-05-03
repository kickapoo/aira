# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime as dt

from django.db import migrations, models

crop_type_parameters = {
    "kiwi": {
        "id": 4,
        "kc_init": 0.4,
        "kc_mid": 1.05,
        "kc_end": 1.05,
        "days_kc_init": 20,
        "days_kc_dev": 70,
        "days_kc_mid": 120,
        "days_kc_late": 60,
        "planting_date": dt.date(1970, 3, 15),
    },
    "olives": {
        "id": 15,
        "kc_init": 0.65,
        "kc_mid": 0.7,
        "kc_end": 0.7,
        "days_kc_init": 30,
        "days_kc_dev": 90,
        "days_kc_mid": 60,
        "days_kc_late": 90,
        "planting_date": dt.date(1970, 3, 15),
    },
    "citrus20": {
        "id": 16,
        "kc_init": 0.85,
        "kc_mid": 0.85,
        "kc_end": 0.85,
        "days_kc_init": 60,
        "days_kc_dev": 90,
        "days_kc_mid": 120,
        "days_kc_late": 95,
        "planting_date": dt.date(1970, 3, 15),
    },
    "citrus50": {
        "id": 17,
        "kc_init": 0.8,
        "kc_mid": 0.8,
        "kc_end": 0.8,
        "days_kc_init": 60,
        "days_kc_dev": 90,
        "days_kc_mid": 120,
        "days_kc_late": 95,
        "planting_date": dt.date(1970, 3, 15),
    },
    "citrus70": {
        "id": 18,
        "kc_init": 0.75,
        "kc_mid": 0.7,
        "kc_end": 0.75,
        "days_kc_init": 60,
        "days_kc_dev": 90,
        "days_kc_mid": 120,
        "days_kc_late": 95,
        "planting_date": dt.date(1970, 3, 15),
    },
    "turf warm": {
        "id": 73,
        "kc_init": 0.8,
        "kc_mid": 0.85,
        "kc_end": 0.85,
        "days_kc_init": 150,
        "days_kc_dev": 40,
        "days_kc_mid": 130,
        "days_kc_late": 45,
        "planting_date": dt.date(1970, 3, 15),
    },
    "turf cool": {
        "id": 74,
        "kc_init": 0.9,
        "kc_mid": 0.85,
        "kc_end": 0.85,
        "days_kc_init": 150,
        "days_kc_dev": 40,
        "days_kc_mid": 130,
        "days_kc_late": 45,
        "planting_date": dt.date(1970, 3, 15),
    },
}


def set_parameter_values(apps, schema_editor):
    CropType = apps.get_model("aira", "CropType")
    for ct_name, ct_parms in crop_type_parameters.items():
        ct = CropType.objects.get(id=ct_parms["id"])
        ct.kc_init = ct_parms["kc_init"]
        ct.kc_mid = ct_parms["kc_mid"]
        ct.kc_end = ct_parms["kc_end"]
        ct.days_kc_init = ct_parms["days_kc_init"]
        ct.days_kc_dev = ct_parms["days_kc_dev"]
        ct.days_kc_mid = ct_parms["days_kc_mid"]
        ct.days_kc_late = ct_parms["days_kc_late"]
        ct.planting_date = ct_parms["planting_date"]
        ct.save()


class Migration(migrations.Migration):

    dependencies = [
        ('aira', '0019_data'),
    ]

    operations = [
        migrations.RemoveField(model_name='croptype', name='kc'),
        migrations.AddField(
            model_name='croptype',
            name='days_kc_dev',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='days_kc_late',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='days_kc_init',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='days_kc_mid',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='kc_end',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='kc_init',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='kc_mid',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='croptype',
            name='planting_date',
            field=models.DateField(default=dt.date(1970, 1, 1)),
            preserve_default=False,
        ),
        migrations.RunPython(set_parameter_values),
    ]
