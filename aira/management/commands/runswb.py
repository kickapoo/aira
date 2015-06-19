from django.core.management.base import BaseCommand

from aira.models import Agrifield
from aira.irma.main import load_meteodata_file_paths, model_run, \
    performance_chart


class Command(BaseCommand):
    help = "Reruns the soil water balance for all fields and caches results."

    def handle(self, *args, **options):
        daily_r_fps, daily_e_fps, hourly_r_fps, hourly_e_fps = \
            load_meteodata_file_paths()
        for agrifield in Agrifield.objects.all():
            # The following try-excepts are an emergency solution for the
            # system to continue to work despite issue #97. Remove after fixing
            # #97.
            try:
                model_run(agrifield, 'NO', daily_r_fps, daily_e_fps, hourly_r_fps,
                          hourly_e_fps, ignore_cache=True)
            except:
                pass
            try:
                model_run(agrifield, 'YES', daily_r_fps, daily_e_fps, hourly_r_fps,
                          hourly_e_fps, ignore_cache=True)
            except:
                pass
            try:
                performance_chart(agrifield, daily_r_fps, daily_e_fps,
                                  ignore_cache=True)
            except:
                pass
