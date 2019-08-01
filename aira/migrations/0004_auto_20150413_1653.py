from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0003_auto_20150413_1640")]

    operations = [
        migrations.RenameField(
            model_name="agrifield", old_name="custom_theta_s", new_name="custom_thetaS"
        )
    ]
