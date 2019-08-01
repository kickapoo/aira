from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0015_agrifield_is_virtual")]

    operations = [
        migrations.AlterModelOptions(
            name="irrigationlog",
            options={
                "ordering": ("-time",),
                "get_latest_by": "time",
                "verbose_name_plural": "Irrigation Logs",
            },
        )
    ]
