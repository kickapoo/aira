from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("aira", "0007_profile_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="supervisor",
            field=models.ForeignKey(
                related_name="supervisor",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="profile",
            name="notification",
            field=models.CharField(
                max_length=2,
                null=True,
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
        ),
    ]
