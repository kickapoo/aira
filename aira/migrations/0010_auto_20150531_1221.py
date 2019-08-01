import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0009_auto_20150516_2040")]

    operations = [
        migrations.AlterField(
            model_name="irrigationlog",
            name="applied_water",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0.0)],
            ),
        )
    ]
