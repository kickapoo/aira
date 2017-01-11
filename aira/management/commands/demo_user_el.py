from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from aira.models import (Profile, Agrifield, IrrigationLog,
                         CropType, IrrigationType)


class Command(BaseCommand):
    help = """Create demo user with credentials
              username: demo
              password: demo
           """

    def handle(self, *args, **options):
        try:
            demo, created = User.objects.get_or_create(username="demo",
                                                       email="anastasiadis.st00@gmail.com")
            demo.set_password('demo')
            demo.is_active = True
            demo.save()
            p, created = Profile.objects.get_or_create(farmer=demo,
                                                       first_name="Aira Demo",
                                                       last_name="Aira Demo",
                                                       address="Arta")
            p.save()

            crop = CropType.objects.all()[6]
            drip = IrrigationType.objects.all()[2]

            # Agrifield with location outside raster
            f, created = Agrifield.objects.get_or_create(owner=demo,
                                                         name="OUTSIDE ARTA RASTER",
                                                         latitude=38,
                                                         longitude=19,
                                                         crop_type=crop,
                                                         irrigation_type=drip,
                                                         area=10000.00,
                                                         use_custom_parameters=False)
            f.save()

            # Agrifield with at least on irrigation log within datasample period
            f, created = Agrifield.objects.get_or_create(owner=demo,
                                                         name="Field with irrigation log",
                                                         latitude=39.15,
                                                         longitude=20.98,
                                                         crop_type=crop,
                                                         irrigation_type=drip,
                                                         area=10000.00,
                                                         use_custom_parameters=False)
            f.save()
            l, created = IrrigationLog.objects.get_or_create(agrifield=f,
                                                             time="2015-02-15 00:00",
                                                             applied_water=23.00)
            l.save()

            # Agrifield with no irrigation log
            f, created = Agrifield.objects.get_or_create(owner=demo,
                                                         name="Field with no irrigation log",
                                                         latitude=39.10,
                                                         longitude=20.92,
                                                         crop_type=crop,
                                                         irrigation_type=drip,
                                                         area=10000.00,
                                                         use_custom_parameters=False)
            f.save()

            # Agrifield with irrigation log outside datasample period
            # Datasample: full December of 2014
            f, created = Agrifield.objects.get_or_create(owner=demo,
                                                         name="Field with log outside dataset",
                                                         latitude=39.12,
                                                         longitude=20.94,
                                                         crop_type=crop,
                                                         irrigation_type=drip,
                                                         area=10000.00,
                                                         use_custom_parameters=False)
            f.save()
            l, created = IrrigationLog.objects.get_or_create(agrifield=f,
                                                             time="2014-02-15 00:00",
                                                             applied_water=23.00)
            l.save()
        except:
            raise CommandError("Use 'python manage.py populate.coeffs' first")
        self.stdout.write('Demo User Added')
