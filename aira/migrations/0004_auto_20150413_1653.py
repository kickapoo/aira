# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("aira", "0003_auto_20150413_1640")]

    operations = [
        migrations.RenameField(
            model_name="agrifield", old_name="custom_theta_s", new_name="custom_thetaS"
        )
    ]
