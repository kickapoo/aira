from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("aira", "0013_auto_20150716_1759")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="notification",
            field=models.CharField(
                default="",
                max_length=3,
                blank=True,
                choices=[
                    ("D", "Day"),
                    ("2D", "2 Days"),
                    ("3D", "3 Days"),
                    ("4D", "4 Days"),
                    ("5D", "5 Days"),
                    ("7D", "Week"),
                    ("10D", "10 Day"),
                    ("30D", "Month"),
                ],
            ),
            preserve_default=True,
        )
    ]
