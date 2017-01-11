from django.core.management.base import BaseCommand

from aira.models import Agrifield
from aira.irma_utils import agripoint_in_raster


class Command(BaseCommand):
    help = "Initiates a recalculation of the model for all fields"

    def handle(self, *args, **options):
        for agrifield in Agrifield.objects.all():
            agrifield.async_execute_swb("YES", True)
