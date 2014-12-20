import os
import csv
from django.conf import settings
from aira.models import IrrigationType


def run():
    print "Starting Irrigation Efficiency Table additions ... "
    croptype_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                                'irr_eff.csv')
    print croptype_csv
    with open(croptype_csv) as f:
        reader = csv.reader(f)
        for row in reader:
            print row[0], row[1]
            _, created = IrrigationType.objects.get_or_create(
                irrt_name=row[0],
                irrt_eff=float(row[1])
            )
    print "Nice work!!! Let populate CropType parameters now"
    print "Finished ... enjoy... "
