import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from aira.models import CropType, IrrigationType


class Command(BaseCommand):
    help = """Populate CropType and IrrigationType tables
              of aira database with essential constant coefficients"""

    def handle(self, *args, **options):
        try:
            croptype_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                                        'croptype.csv')
            irrt_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                                    'irr_eff.csv')

            with open(irrt_csv) as f:
                reader = csv.reader(f)
                for row in reader:
                    _, created = IrrigationType.objects.get_or_create(
                                    name=row[0],
                                    efficiency=float(row[1]),
                                )
            with open(croptype_csv) as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    _, created = CropType.objects.get_or_create(
                                    name=str(row[0]),
                                    root_depth_min=float(row[1]),
                                    root_depth_max=float(row[2]),
                                    max_allow_depletion=float(row[3]),
                                    kc=float(row[4]),
                                    fek_category=int(row[5]),
                                )
            self.stdout.write('Aira Coefficients Eng Vr import: Success')
        except Exception as e:
            print(e)
            raise CommandError("Error during updating database")
