# Note
# A minor patch command that iter the list of database Agrifields.
# If Agrifield is not in mask raster (in aira case Arta) force update
# of latitude and longitude with Arta city coordinates.
from django.core.management.base import BaseCommand
from aira.models import Agrifield


class Command(BaseCommand):
    help = "Patch Update outside study agrifield to have Arta center."

    def handle(self, *args, **options):
        for agrifield in Agrifield.objects.all():
            if not agrifield.in_raster():
                agrifield.latitude = 39.15
                agrifield.longitude = 20.98
                agrifield.save()
        self.stdout.write('Agrifields are updated... :)')
