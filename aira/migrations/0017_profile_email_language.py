from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("aira", "0016_auto_20160505_1828")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="email_language",
            field=models.CharField(
                default="en",
                max_length=3,
                choices=[("en", "English"), ("el", "Ελληνικά")],
            ),
        )
    ]
