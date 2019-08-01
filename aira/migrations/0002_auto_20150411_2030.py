from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="agrifield",
            name="custom_field_capacity",
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="agrifield", name="area", field=models.FloatField()
        ),
    ]
