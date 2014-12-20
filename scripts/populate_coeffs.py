from __future__ import print_function
import os
import csv
from django.conf import settings
from aira.models import IrrigationType, CropType


def run():
    print("Starting with Irrigation Type ...")
    irrt_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                            'irr_eff.csv')
    with open(irrt_csv) as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = IrrigationType.objects.get_or_create(
                irrt_name=row[0],
                irrt_eff=float(row[1])
            )
    print("Continue with CropType...")
    croptype_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                                'croptype.csv')
    with open(croptype_csv) as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = CropType.objects.get_or_create(
                ct_name=row[0],
                ct_coeff=float(row[1]),
                ct_rd=float(row[2])
            )
    print("Your aira.db is now update with all essential coefficients")
