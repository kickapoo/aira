from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Agrifield",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(default="i.e. MyField1", max_length=255)),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("area", models.FloatField(null=True, blank=True)),
                (
                    "irrigation_optimizer",
                    models.FloatField(
                        default=1.0,
                        choices=[
                            (0.5, "IRT (50% Inet)"),
                            (0.75, "IRT (75% Inet)"),
                            (1.0, "IRT (100% Inet)"),
                        ],
                    ),
                ),
                ("use_custom_parameters", models.BooleanField(default=False)),
                ("custom_kc", models.FloatField(null=True, blank=True)),
                ("custom_root_depth_max", models.FloatField(null=True, blank=True)),
                ("custom_root_depth_min", models.FloatField(null=True, blank=True)),
                (
                    "custom_max_allow_depletion",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                ("custom_efficiency", models.FloatField(null=True, blank=True)),
                (
                    "custom_irrigation_optimizer",
                    models.FloatField(null=True, blank=True),
                ),
            ],
            options={"ordering": ("name", "area"), "verbose_name_plural": "Agrifields"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CropType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("root_depth_max", models.FloatField()),
                ("root_depth_min", models.FloatField()),
                (
                    "max_allow_depletion",
                    models.DecimalField(max_digits=6, decimal_places=2),
                ),
                # Note: kc doesn't actually have a default of 0.7. It's without default.
                # The reason why we added this dummy default in the migration was to
                # make it possible to reverse migration 0020, which abolishes it.
                # Migration 0020 is not reversible on production (i.e. you can't migrate
                # back from 0020 to 0019 and expect things to work properly), but making
                # it reversible enables us to bisect the history in order to find which
                # commit introduced an error. Antonis Christofides, 2020-03-31.
                ("kc", models.FloatField(default=0.7)),
                ("fek_category", models.IntegerField()),
            ],
            options={"ordering": ("name",), "verbose_name_plural": "Crop Types"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IrrigationLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("time", models.DateTimeField()),
                ("applied_water", models.IntegerField()),
                (
                    "agrifield",
                    models.ForeignKey(to="aira.Agrifield", on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("time",),
                "get_latest_by": "time",
                "verbose_name_plural": "Irrigation Logs",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IrrigationType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("efficiency", models.FloatField()),
            ],
            options={"ordering": ("name",), "verbose_name_plural": "Irrigation Types"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255, blank=True)),
                (
                    "farmer",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"verbose_name_plural": "Profiles"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="agrifield",
            name="crop_type",
            field=models.ForeignKey(to="aira.CropType", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="agrifield",
            name="irrigation_type",
            field=models.ForeignKey(to="aira.IrrigationType", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="agrifield",
            name="owner",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
