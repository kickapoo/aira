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
                    _, created = IrrigationType.objects.get_or_create(irrt_name=row[0],
                                                                      irrt_eff=float(row[1]))
            with open(croptype_csv) as f:
                reader = csv.reader(f)
                for row in reader:
                    _, created = CropType.objects.get_or_create(ct_name=row[0],
                                                                ct_coeff=float(row[1]),
                                                                ct_rd=float(row[2]),
                                                                ct_kc=float(row[3]),
                                                                ct_fek=int(row[4]),
                                                                )
        except:
            raise CommandError("Use 'makemigrations aira' to create aira tables")

        self.stdout.write('Aira database is successfully updated')
