#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from aira.models import CropType, IrrigationType


class Command(BaseCommand):
    help = """Populate CropType and IrrigationType tables
              of aira database with essential constant coefficients
              as Greek_name (English_name) """

    def handle(self, *args, **options):
        try:
            croptype_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                                        'croptype_el.csv')
            irrt_csv = os.path.join(settings.AIRA_PARAMETERS_FILE_DIR,
                                    'irr_eff_el.csv')

            with open(irrt_csv) as f:
                reader = csv.reader(f)
                for row in reader:
                    irr_type_el = "{} ({})".format(row[1], row[0])
                    if IrrigationType.objects.filter(name=row[0]).exists():
                        irr_type = IrrigationType.objects.get(name=row[0])
                        irr_type.name = irr_type_el
                        irr_type.save()
                    else:
                        irr_type = IrrigationType.objects.create(
                                                name=irr_type_el,
                                                efficiency=float(row[2]))


            with open(croptype_csv) as f:
                reader = csv.reader(f)
                reader.next()
                for row in reader:
                    crop_type_el = "{} ({})".format(row[1], row[0])
                    if CropType.objects.filter(name=row[0]).exists():
                        crop_type = CropType.objects.get(name=row[0])
                        crop_type.name = crop_type_el
                        crop_type.save()
                    else:
                        crop_type = CropType.objects.create(
                                 name=crop_type_el,
                                 root_depth_min=float(row[2]),
                                 root_depth_max=float(row[3]),
                                 max_allow_depletion=float(row[4]),
                                 kc=float(row[5]),
                                 fek_category=int(row[6]),)
        except:
            raise CommandError(
                "Use 'makemigrations aira' to create aira tables")

        self.stdout.write("CropType and IrrigationType name reference is update as 'Greek name (English name)'")
