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
            demo, created = User.objects.get_or_create(username="demo")
            demo.set_password('demo')
            demo.is_active = True
            demo.save()
            p, created = Profile.objects.get_or_create(farmer=demo,
                                                       first_name="Aira Demo",
                                                       last_name="Aira Demo",
                                                       address="Arta")
            p.save()

            tomato = CropType.objects.filter(ct_name="Tomato").first()
            drip = IrrigationType.objects.filter(irrt_name="Drip irrigation").first()

            f, created = Agrifield.objects.get_or_create(owner=demo,
                                                         name="Close to Arta",
                                                         latitude=39.15,
                                                         longitude=20.98,
                                                         ct=tomato,
                                                         irrt=drip,
                                                         area=2800.00)
            f.save()
            l, created = IrrigationLog.objects.get_or_create(agrifield=f,
                                                             time="2014-12-02 00:00",
                                                             water_amount=23.00)
            l.save()
        except:
            raise CommandError("Use 'python manage.py populate.coeffs' first")
        self.stdout.write('Demo User Added')
