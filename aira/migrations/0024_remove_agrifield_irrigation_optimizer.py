from django.db import migrations


def check_irrigation_optimizer(apps, schema_editor):
    Agrifield = apps.get_model("aira", "Agrifield")
    if Agrifield.objects.exclude(irrigation_optimizer=0.5).exists():
        raise ValueError(
            "I wanted to remove field Agrifield.irrigation_optimizer, which should "
            "be useless as it always has a value of 0.5. However, I found an instance "
            "where it has a different value. Cowardly refusing to continue."
        )


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("aira", "0023_agrifield_soil_analysis")]

    operations = [
        migrations.RunPython(check_irrigation_optimizer, do_nothing),
        migrations.RemoveField(model_name="agrifield", name="irrigation_optimizer"),
    ]
