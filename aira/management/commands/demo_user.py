from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError

from aira.models import Agrifield, CropType, IrrigationLog, IrrigationType


class Command(BaseCommand):
    help = """Create demo user with credentials
              username: demo
              password: demo
           """

    def handle(self, *args, **options):
        try:
            demo, created = User.objects.get_or_create(
                username="demo", email="demo@aira.com"
            )
            demo.set_password("demo")
            demo.is_active = True
            demo.save()
            demo.profile.first_name = "Aira Demo"
            demo.profile.last_name = "Aira Demo"
            demo.profile.address = "Aira"
            demo.save()

            crop = CropType.objects.all()[6]
            drip = IrrigationType.objects.all()[2]

            # Agrifield with location outside raster
            f, created = Agrifield.objects.get_or_create(
                owner=demo,
                name="OUTSIDE ARTA RASTER",
                location=Point(19.0, 38.0),
                crop_type=crop,
                irrigation_type=drip,
                area=10000.00,
                use_custom_parameters=False,
            )
            f.save()

            # Agrifield with at least on irrigation log within datasample period
            f, created = Agrifield.objects.get_or_create(
                owner=demo,
                name="Field with irrigation log",
                location=Point(20.98, 39.15),
                crop_type=crop,
                irrigation_type=drip,
                area=10000.00,
                use_custom_parameters=False,
            )
            f.save()
            l, created = IrrigationLog.objects.get_or_create(
                agrifield=f, time="2015-02-15 00:00Z", applied_water=23.00
            )
            l.save()

            # Agrifield with no irrigation log
            f, created = Agrifield.objects.get_or_create(
                owner=demo,
                name="Field with no irrigation log",
                location=Point(20.92, 39.10),
                crop_type=crop,
                irrigation_type=drip,
                area=10000.00,
                use_custom_parameters=False,
            )
            f.save()

            # Agrifield with irrigation log outside datasample period
            # Datasample: full December of 2014
            f, created = Agrifield.objects.get_or_create(
                owner=demo,
                name="Field with log outside dataset",
                location=Point(20.94, 39.12),
                crop_type=crop,
                irrigation_type=drip,
                area=10000.00,
                use_custom_parameters=False,
            )
            f.save()
            l, created = IrrigationLog.objects.get_or_create(
                agrifield=f, time="2014-02-15 00:00Z", applied_water=23.00
            )
            l.save()
            self.stdout.write("Aira Demo user import: Success")
        except Exception as e:
            print(e)
            raise CommandError("Error during importing Demo user in database")
