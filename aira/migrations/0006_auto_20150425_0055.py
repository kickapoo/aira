from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0005_auto_20150419_1109")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="farmer",
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),
        )
    ]
