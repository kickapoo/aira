from django.core.management.base import BaseCommand

from aira.models import Agrifield
from aira.irma.main import agripoint_in_raster


class Command(BaseCommand):
    help = "Initiates a recalculation of the model for all fields"

    def handle(self, *args, **options):
        for agrifield in Agrifield.objects.all():
            if agripoint_in_raster(agrifield):
                agrifield.execute_model()
