from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0014_auto_20151031_1716")]

    operations = [
        migrations.AddField(
            model_name="agrifield",
            name="is_virtual",
            field=models.NullBooleanField(
                default=None, choices=[(True, "Yes"), (False, "No"), (None, "-")]
            ),
            preserve_default=True,
        )
    ]
