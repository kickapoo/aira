from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0024_remove_agrifield_irrigation_optimizer")]

    operations = [
        migrations.AlterField(
            model_name="croptype", name="max_allow_depletion", field=models.FloatField()
        ),
        migrations.RenameField(
            model_name="agrifield",
            old_name="custom_max_allow_depletion",
            new_name="custom_max_allowed_depletion",
        ),
        migrations.RenameField(
            model_name="croptype",
            old_name="max_allow_depletion",
            new_name="max_allowed_depletion",
        ),
    ]
